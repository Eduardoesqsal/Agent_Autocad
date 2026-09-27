using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Geometry;
using AcadColor = Autodesk.AutoCAD.Colors.Color;
using ColorMethod = Autodesk.AutoCAD.Colors.ColorMethod;
using DrawingFont = System.Drawing.Font;

namespace CodexAutoCADPalette
{
    public sealed class CodexPaletteControl : UserControl
    {
        private const string ProjectRoot = @"C:\Users\eduar\Music\Agent_Autocad";
        private FlowLayoutPanel chatFlow;
        private TextBox promptInput;
        private Button sendButton;

        private sealed class LayerSpec
        {
            public LayerSpec(string name, short color)
            {
                Name = name;
                Color = color;
            }

            public string Name { get; private set; }

            public short Color { get; private set; }
        }

        private static readonly LayerSpec[] BaseLayers =
        {
            new LayerSpec("TERRENO", 3),
            new LayerSpec("CUADRO_DATOS", 2),
            new LayerSpec("ANOTACIONES", 2),
            new LayerSpec("COLINDANTES", 7),
            new LayerSpec("VERTICES", 1),
            new LayerSpec("RETICULA", 8),
            new LayerSpec("NOTAS", 6)
        };

        public CodexPaletteControl()
        {
            BuildUi();
        }

        public static void CreateBaseLayers()
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            Database db = doc.Database;
            using (doc.LockDocument())
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                LayerTable layerTable = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForRead);

                foreach (LayerSpec spec in BaseLayers)
                {
                    if (!layerTable.Has(spec.Name))
                    {
                        layerTable.UpgradeOpen();
                        using (LayerTableRecord layer = new LayerTableRecord())
                        {
                            layer.Name = spec.Name;
                            layer.Color = AcadColor.FromColorIndex(ColorMethod.ByAci, spec.Color);
                            layerTable.Add(layer);
                            tr.AddNewlyCreatedDBObject(layer, true);
                        }
                    }
                    else
                    {
                        LayerTableRecord layer =
                            (LayerTableRecord)tr.GetObject(layerTable[spec.Name], OpenMode.ForWrite);
                        layer.Color = AcadColor.FromColorIndex(ColorMethod.ByAci, spec.Color);
                    }
                }

                tr.Commit();
            }

            doc.Editor.WriteMessage("\nCapas base Codex creadas/actualizadas.");
        }

        public static void CreateUtmGrid()
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            Editor editor = doc.Editor;
            PromptDoubleOptions options = new PromptDoubleOptions("\nDistancia entre cruces UTM: ")
            {
                AllowNegative = false,
                AllowZero = false,
                AllowNone = false,
                DefaultValue = 10.0
            };
            PromptDoubleResult result = editor.GetDouble(options);
            if (result.Status != PromptStatus.OK)
            {
                editor.WriteMessage("\nReticula cancelada.");
                return;
            }

            CreateUtmGrid(result.Value);
        }

        public static void CreateUtmGrid(double spacing)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            Editor editor = doc.Editor;
            Database db = doc.Database;

            using (doc.LockDocument())
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                EnsureLayer(db, tr, "RETICULA", 8);
                BlockTable blockTable = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);

                Extents3d extents = GetDrawableExtents(db);
                double minX = Math.Floor(extents.MinPoint.X / spacing) * spacing - spacing;
                double maxX = Math.Ceiling(extents.MaxPoint.X / spacing) * spacing + spacing;
                double minY = Math.Floor(extents.MinPoint.Y / spacing) * spacing - spacing;
                double maxY = Math.Ceiling(extents.MaxPoint.Y / spacing) * spacing + spacing;
                double half = Math.Max(1.0, spacing * 0.1);
                double textHeight = Math.Max(0.3, Math.Min(1.0, spacing * 0.05));

                int total = 0;
                for (double x = minX; x <= maxX; x += spacing)
                {
                    for (double y = minY; y <= maxY; y += spacing)
                    {
                        AppendLine(modelSpace, tr, x - half, y, x + half, y, "RETICULA");
                        AppendLine(modelSpace, tr, x, y - half, x, y + half, "RETICULA");
                        total++;
                    }
                }

                for (double x = minX; x <= maxX; x += spacing)
                {
                    AppendText(modelSpace, tr, x.ToString("0.###"), x, minY - spacing * 0.5, textHeight, Math.PI / 2.0);
                }

                for (double y = minY; y <= maxY; y += spacing)
                {
                    AppendText(modelSpace, tr, y.ToString("0.###"), minX - spacing * 0.5, y, textHeight, 0.0);
                }

                tr.Commit();
                editor.WriteMessage(
                    string.Format(
                        "\nReticula UTM creada cada {0:0.###} m con {1} cruces.",
                        spacing,
                        total));
            }

            ZoomExtents();
        }

        public static void ZoomExtents()
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                doc.SendStringToExecute("_.ZOOM _E ", true, false, false);
            }
        }

        private void BuildUi()
        {
            System.Drawing.Color shell = System.Drawing.Color.FromArgb(24, 25, 27);
            System.Drawing.Color surface = System.Drawing.Color.FromArgb(34, 35, 38);
            System.Drawing.Color surfaceAlt = System.Drawing.Color.FromArgb(42, 43, 47);
            System.Drawing.Color border = System.Drawing.Color.FromArgb(67, 70, 76);
            System.Drawing.Color accent = System.Drawing.Color.FromArgb(48, 151, 209);

            BackColor = shell;
            ForeColor = System.Drawing.Color.Gainsboro;
            Padding = new Padding(12);

            TableLayoutPanel root = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                BackColor = BackColor,
                ColumnCount = 1,
                RowCount = 4
            };

            root.RowStyles.Add(new RowStyle(SizeType.Absolute, 86));
            root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            root.RowStyles.Add(new RowStyle(SizeType.Absolute, 104));
            root.RowStyles.Add(new RowStyle(SizeType.Absolute, 46));

            Label title = new Label
            {
                Text = "Codex CAD Agent",
                Dock = DockStyle.Fill,
                Font = new DrawingFont("Segoe UI Semibold", 14, FontStyle.Bold),
                ForeColor = System.Drawing.Color.White,
                TextAlign = ContentAlignment.MiddleLeft
            };

            Label subtitle = new Label
            {
                Text = "Prompt inteligente para dibujo arquitectonico y CAD",
                Dock = DockStyle.Fill,
                Font = new DrawingFont("Segoe UI", 9),
                ForeColor = System.Drawing.Color.FromArgb(185, 190, 198),
                TextAlign = ContentAlignment.MiddleLeft
            };

            Label status = new Label
            {
                Text = "AutoCAD 2021 | metros | listo",
                Dock = DockStyle.Bottom,
                Font = new DrawingFont("Segoe UI", 8),
                ForeColor = accent,
                TextAlign = ContentAlignment.MiddleLeft,
                Height = 18
            };

            Panel header = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = surface
            };
            header.Padding = new Padding(14, 8, 14, 8);
            header.Paint += delegate(object sender, PaintEventArgs e)
            {
                using (Pen pen = new Pen(accent, 3))
                {
                    e.Graphics.DrawLine(pen, 0, 0, 0, header.Height);
                }
                using (Pen pen = new Pen(border, 1))
                {
                    e.Graphics.DrawLine(pen, 0, header.Height - 1, header.Width, header.Height - 1);
                }
            };
            header.Controls.Add(status);
            header.Controls.Add(subtitle);
            header.Controls.Add(title);
            title.Height = 34;
            title.Dock = DockStyle.Top;
            subtitle.Height = 22;
            subtitle.Dock = DockStyle.Top;

            root.Controls.Add(header, 0, 0);

            Panel transcriptPanel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = surface,
                Padding = new Padding(12),
                Margin = new Padding(0, 10, 0, 0)
            };
            transcriptPanel.Paint += delegate(object sender, PaintEventArgs e)
            {
                using (Pen pen = new Pen(border, 1))
                {
                    e.Graphics.DrawRectangle(pen, 0, 0, transcriptPanel.Width - 1, transcriptPanel.Height - 1);
                }
            };

            chatFlow = new FlowLayoutPanel
            {
                Dock = DockStyle.Fill,
                BackColor = surface,
                AutoScroll = true,
                FlowDirection = System.Windows.Forms.FlowDirection.TopDown,
                WrapContents = false,
                Padding = new Padding(0)
            };
            chatFlow.Resize += delegate { RelayoutBubbles(); };
            transcriptPanel.Controls.Add(chatFlow);
            root.Controls.Add(transcriptPanel, 0, 1);

            Panel inputPanel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = surfaceAlt,
                Padding = new Padding(10),
                Margin = new Padding(0, 10, 0, 0)
            };
            inputPanel.Paint += delegate(object sender, PaintEventArgs e)
            {
                using (Pen pen = new Pen(border, 1))
                {
                    e.Graphics.DrawRectangle(pen, 0, 0, inputPanel.Width - 1, inputPanel.Height - 1);
                }
            };

            promptInput = new TextBox
            {
                Dock = DockStyle.Fill,
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                BackColor = surfaceAlt,
                ForeColor = System.Drawing.Color.White,
                BorderStyle = BorderStyle.None,
                Font = new DrawingFont("Segoe UI", 10),
                Margin = new Padding(0)
            };
            promptInput.KeyDown += PromptInputKeyDown;
            inputPanel.Controls.Add(promptInput);
            root.Controls.Add(inputPanel, 0, 2);

            sendButton = CreateButton("Enviar a AutoCAD  (Ctrl+Enter)", SendPrompt);
            root.Controls.Add(sendButton, 0, 3);

            Controls.Add(root);
            AppendAssistantMessage("Listo. Pide un plano arquitectonico normativo, poligonos por origen, reticula UTM, cotas, texto, edicion de ultima entidad o comandos directos con cad:.");
            AppendAssistantMessage("Ejemplos: \"crea un plano arquitectonico de acuerdo a normas\" | \"poligono de 10 x 20 origen 100,200\" | \"poligono regular 6 lados radio 5 origen 0,0\".");
        }

        private static Button CreateButton(string text, Action action)
        {
            Button button = new Button
            {
                Text = text,
                Dock = DockStyle.Fill,
                FlatStyle = FlatStyle.Flat,
                BackColor = System.Drawing.Color.FromArgb(48, 151, 209),
                ForeColor = System.Drawing.Color.White,
                Font = new DrawingFont("Segoe UI Semibold", 9, FontStyle.Bold),
                Margin = new Padding(0, 10, 0, 0)
            };
            button.FlatAppearance.BorderSize = 0;
            button.FlatAppearance.MouseOverBackColor = System.Drawing.Color.FromArgb(67, 170, 224);
            button.FlatAppearance.MouseDownBackColor = System.Drawing.Color.FromArgb(35, 117, 166);
            button.Click += delegate { action(); };
            return button;
        }

        private void PromptInputKeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter && e.Control)
            {
                e.SuppressKeyPress = true;
                SendPrompt();
            }
        }

        private void SendPrompt()
        {
            string prompt = promptInput.Text.Trim();
            if (prompt.Length == 0)
            {
                return;
            }

            AppendUserMessage(prompt);
            promptInput.Clear();

            try
            {
                string result = ExecutePrompt(prompt);
                AppendAssistantMessage(result);
            }
            catch (System.Exception ex)
            {
                AppendAssistantMessage("Error: " + ex.Message);
                WriteMessage("\nCodex error: " + ex.Message);
            }
        }

        private void AppendUserMessage(string text)
        {
            AppendRichMessage("Tu", text, System.Drawing.Color.FromArgb(142, 202, 230), System.Drawing.Color.White);
        }

        private void AppendAssistantMessage(string text)
        {
            AppendRichMessage("Codex", text, System.Drawing.Color.FromArgb(80, 220, 140), System.Drawing.Color.FromArgb(226, 229, 234));
        }

        private void AppendRichMessage(string author, string text, System.Drawing.Color authorColor, System.Drawing.Color bodyColor)
        {
            bool isUser = author == "Tu";
            Panel bubble = new Panel
            {
                BackColor = isUser ? System.Drawing.Color.FromArgb(41, 84, 112) : System.Drawing.Color.FromArgb(43, 45, 50),
                Padding = new Padding(12, 8, 12, 10),
                Margin = isUser ? new Padding(52, 4, 4, 10) : new Padding(4, 4, 52, 10),
                Tag = "bubble"
            };

            Label authorLabel = new Label
            {
                Text = author,
                Dock = DockStyle.Top,
                Height = 18,
                Font = new DrawingFont("Segoe UI Semibold", 8, FontStyle.Bold),
                ForeColor = authorColor
            };

            Label bodyLabel = new Label
            {
                Text = text,
                Dock = DockStyle.Fill,
                AutoSize = false,
                Font = new DrawingFont("Segoe UI", 9, FontStyle.Regular),
                ForeColor = bodyColor
            };

            bubble.Controls.Add(bodyLabel);
            bubble.Controls.Add(authorLabel);
            chatFlow.Controls.Add(bubble);
            SizeBubble(bubble);
            chatFlow.ScrollControlIntoView(bubble);
        }

        private void RelayoutBubbles()
        {
            foreach (Control control in chatFlow.Controls)
            {
                Panel bubble = control as Panel;
                if (bubble != null && Convert.ToString(bubble.Tag) == "bubble")
                {
                    SizeBubble(bubble);
                }
            }
        }

        private void SizeBubble(Panel bubble)
        {
            int width = Math.Max(220, chatFlow.ClientSize.Width - 74);
            bubble.Width = width;
            Label body = bubble.Controls[0] as Label;
            if (body != null)
            {
                int labelWidth = width - bubble.Padding.Left - bubble.Padding.Right;
                Size preferred = TextRenderer.MeasureText(
                    body.Text,
                    body.Font,
                    new Size(labelWidth, 0),
                    TextFormatFlags.WordBreak | TextFormatFlags.TextBoxControl);
                body.Height = Math.Max(24, preferred.Height + 4);
                bubble.Height = body.Height + 42;
            }
        }

        private static string ExecutePrompt(string prompt)
        {
            string agentReply;
            if (TryExecuteAgentPlan(prompt, out agentReply))
            {
                return agentReply;
            }

            string normalized = Normalize(prompt);
            List<double> numbers = ExtractNumbers(prompt);

            if (normalized.StartsWith("cad:") || normalized.StartsWith("comando:"))
            {
                string command = prompt.Substring(prompt.IndexOf(':') + 1).Trim();
                SendCadCommand(command);
                return "Ejecute el comando CAD indicado.";
            }

            if (ContainsAny(normalized, "ayuda", "skills", "que puedes", "opciones"))
            {
                return "Skills: plano arquitectonico normativo, linea, polilinea abierta, poligono por pares, poligono por origen y medidas, poligono regular por lados/radio/origen, rectangulo, circulo, texto, capas, reticula UTM, cota, anotar distancias, etiquetar vertices, borrar ultima, mover ultima, copiar ultima, rotar ultima, zoom, guardar, y comandos directos con cad:.";
            }

            if (ContainsAny(normalized, "plano arquitectonico", "planta arquitectonica", "plano de casa", "casa habitacion", "normas"))
            {
                CreateArchitecturalPlan();
                return "Genere una planta arquitectonica base 10x8 m con muros, espacios, vanos, puertas, ventanas, cotas, norte y notas normativas editables.";
            }

            if (ContainsAny(normalized, "capas", "layers"))
            {
                CreateBaseLayers();
                return "Cree/actualice las capas base del proyecto.";
            }

            if (ContainsAny(normalized, "zoom", "extents", "extension", "extensiones"))
            {
                ZoomExtents();
                return "Ejecute Zoom Extents.";
            }

            if (ContainsAny(normalized, "guardar", "salvar", "save"))
            {
                SaveDrawing();
                return "Guarde el dibujo activo.";
            }

            if (ContainsAny(normalized, "borrar ultima", "eliminar ultima", "borra ultima"))
            {
                DeleteLastEntity();
                return "Borre la ultima entidad del modelo.";
            }

            if (ContainsAny(normalized, "mover ultima", "mueve ultima"))
            {
                if (numbers.Count < 2)
                {
                    return "Para mover necesito dx,dy. Ejemplo: mover ultima 2,0.";
                }

                TransformLastEntity(Matrix3d.Displacement(new Vector3d(numbers[0], numbers[1], 0)));
                return "Movi la ultima entidad.";
            }

            if (ContainsAny(normalized, "copiar ultima", "copia ultima"))
            {
                if (numbers.Count < 2)
                {
                    return "Para copiar necesito dx,dy. Ejemplo: copiar ultima 5,0.";
                }

                CopyLastEntity(numbers[0], numbers[1]);
                return "Copie la ultima entidad.";
            }

            if (ContainsAny(normalized, "rotar ultima", "rota ultima"))
            {
                if (numbers.Count < 1)
                {
                    return "Para rotar necesito angulo. Ejemplo: rotar ultima 45.";
                }

                double cx = numbers.Count >= 3 ? numbers[1] : 0;
                double cy = numbers.Count >= 3 ? numbers[2] : 0;
                TransformLastEntity(Matrix3d.Rotation(DegToRad(numbers[0]), Vector3d.ZAxis, new Point3d(cx, cy, 0)));
                return "Rote la ultima entidad.";
            }

            if (ContainsAny(normalized, "reticula", "utm", "grid"))
            {
                if (numbers.Count == 0)
                {
                    return "Indica el espaciado. Ejemplo: reticula utm cada 10.";
                }

                CreateUtmGrid(numbers[0]);
                return string.Format("Genere reticula UTM cada {0:0.###} m.", numbers[0]);
            }

            if (ContainsAny(normalized, "cota", "dimension", "acotar"))
            {
                if (numbers.Count < 4)
                {
                    return "Para una cota necesito x1,y1,x2,y2. Ejemplo: cota de 0,0 a 10,0.";
                }

                CreateAlignedDimension(numbers[0], numbers[1], numbers[2], numbers[3]);
                return "Cree la cota alineada.";
            }

            if (ContainsAny(normalized, "anotar distancias", "distancias lados", "medidas lados"))
            {
                AnnotateDistances();
                return "Anote distancias de lineas y polilineas.";
            }

            if (ContainsAny(normalized, "etiquetar vertices", "vertices", "vértices"))
            {
                LabelLastPolylineVertices();
                return "Etiquete vertices de la ultima polilinea.";
            }

            if (ContainsAny(normalized, "texto", "text"))
            {
                if (numbers.Count < 2)
                {
                    return "Para texto necesito x,y. Ejemplo: texto \"NORTE\" en 5,8 altura 0.5.";
                }

                string textValue = ExtractQuotedText(prompt);
                if (textValue.Length == 0)
                {
                    textValue = TextAfterKeyword(prompt, "texto");
                }

                double height = numbers.Count >= 3 ? numbers[2] : 0.6;
                CreateText(textValue.Length == 0 ? "TEXTO" : textValue, numbers[0], numbers[1], height, 0, "NOTAS");
                return "Inserte el texto.";
            }

            if (ContainsAny(normalized, "rectangulo", "rectangle"))
            {
                if (numbers.Count >= 4)
                {
                    CreateRectangle(numbers[0], numbers[1], numbers[2], numbers[3], "TERRENO");
                    return "Dibuje el rectangulo.";
                }

                if (numbers.Count >= 2)
                {
                    CreateRectangle(0, 0, numbers[0], numbers[1], "TERRENO");
                    return "Dibuje el rectangulo desde 0,0.";
                }

                CreateRectangle(0, 0, 10, 6, "TERRENO");
                return "Dibuje un rectangulo base 10 x 6 desde 0,0.";
            }

            if (ContainsAny(normalized, "poligono", "terreno", "lote", "predio", "parcela", "solar", "cuadrado", "triangulo", "hexagono", "octagono"))
            {
                if (ContainsAny(normalized, "triangulo"))
                {
                    double radius = numbers.Count > 0 ? numbers[0] : 5.0;
                    Point2d origin = ExtractOrigin(prompt, numbers, numbers.Count >= 3 ? 1 : 99);
                    CreateRegularPolygon(3, radius, origin.X, origin.Y, "TERRENO");
                    return "Dibuje un triangulo regular. Use 'radio' u 'origen' si quieres controlarlo mejor.";
                }

                if (ContainsAny(normalized, "hexagono"))
                {
                    double radius = numbers.Count > 0 ? numbers[0] : 5.0;
                    Point2d origin = ExtractOrigin(prompt, numbers, numbers.Count >= 3 ? 1 : 99);
                    CreateRegularPolygon(6, radius, origin.X, origin.Y, "TERRENO");
                    return "Dibuje un hexagono regular.";
                }

                if (ContainsAny(normalized, "octagono"))
                {
                    double radius = numbers.Count > 0 ? numbers[0] : 5.0;
                    Point2d origin = ExtractOrigin(prompt, numbers, numbers.Count >= 3 ? 1 : 99);
                    CreateRegularPolygon(8, radius, origin.X, origin.Y, "TERRENO");
                    return "Dibuje un octagono regular.";
                }

                if (!ContainsAny(normalized, "irregular") && ContainsAny(normalized, "regular", "lados"))
                {
                    int sides = ExtractIntAfter(normalized, "lados", numbers.Count > 0 ? (int)Math.Round(numbers[0]) : 6);
                    double radius = ExtractDoubleAfter(normalized, "radio", numbers.Count > 1 ? numbers[1] : 5.0);
                    Point2d origin = ExtractOrigin(prompt, numbers, Math.Min(numbers.Count - 2, 2));
                    if (sides < 3)
                    {
                        return "Un poligono regular necesita al menos 3 lados.";
                    }

                    CreateRegularPolygon(sides, radius, origin.X, origin.Y, "TERRENO");
                    return string.Format("Dibuje poligono regular de {0} lados con radio {1:0.###} desde origen {2:0.###},{3:0.###}.", sides, radius, origin.X, origin.Y);
                }

                if (numbers.Count >= 4)
                {
                    if (ContainsAny(normalized, "origen", "desde"))
                    {
                        double width = numbers[0];
                        double height = numbers[1];
                        Point2d origin = ExtractOrigin(prompt, numbers, 2);
                        CreateRectangle(origin.X, origin.Y, origin.X + width, origin.Y + height, "TERRENO");
                        return string.Format("Dibuje poligono rectangular de {0:0.###} x {1:0.###} desde origen {2:0.###},{3:0.###}.", width, height, origin.X, origin.Y);
                    }

                    if (numbers.Count % 2 == 0)
                    {
                        bool closed = !ContainsAny(normalized, "abierta", "abierto", "sin cerrar");
                        CreatePolyline(numbers, closed, "TERRENO");
                        return closed ? "Dibuje el poligono con los vertices indicados." : "Dibuje la polilinea abierta con los vertices indicados.";
                    }
                }

                if (numbers.Count >= 2)
                {
                    double width = numbers[0];
                    double height = numbers[1];
                    Point2d origin = ExtractOrigin(prompt, numbers, 99);
                    CreateRectangle(origin.X, origin.Y, origin.X + width, origin.Y + height, "TERRENO");
                    return string.Format("Dibuje un poligono rectangular de {0:0.###} x {1:0.###} desde {2:0.###},{3:0.###}.", width, height, origin.X, origin.Y);
                }

                if (numbers.Count == 1)
                {
                    double size = numbers[0];
                    CreateRectangle(0, 0, size, size, "TERRENO");
                    return string.Format("Dibuje un poligono cuadrado de {0:0.###} x {0:0.###} desde 0,0.", size);
                }

                CreateRectangle(0, 0, 10, 10, "TERRENO");
                return "Dibuje un poligono base de 10 x 10 desde 0,0. Puedes decir 'poligono de 12 x 20 origen 100,200' para controlarlo.";
            }

            if (ContainsAny(normalized, "circulo", "circle"))
            {
                if (numbers.Count < 3)
                {
                    if (numbers.Count == 1)
                    {
                        CreateCircle(0, 0, numbers[0], "TERRENO");
                        return "Dibuje un circulo con centro 0,0 usando el radio indicado.";
                    }

                    return "Para un circulo necesito centro y radio, o solo radio. Ejemplo: circulo en 5,5 radio 2.";
                }

                CreateCircle(numbers[0], numbers[1], numbers[2], "TERRENO");
                return "Dibuje el circulo.";
            }

            if (ContainsAny(normalized, "linea", "line"))
            {
                if (numbers.Count < 4)
                {
                    if (numbers.Count >= 1)
                    {
                        CreateLine(0, 0, numbers[0], 0, "TERRENO");
                        return "Dibuje una linea desde 0,0 con la longitud indicada sobre X.";
                    }

                    CreateLine(0, 0, 10, 0, "TERRENO");
                    return "Dibuje una linea base de 10 m desde 0,0.";
                }

                CreateLine(numbers[0], numbers[1], numbers[2], numbers[3], "TERRENO");
                return "Dibuje la linea.";
            }

            if (ContainsAny(normalized, "comando mcp", "servidor mcp", "mcp"))
            {
                CopyMcpCommand();
                return "Copie el comando MCP al portapapeles.";
            }

            if (ContainsAny(normalized, "abrir carpeta", "carpeta proyecto"))
            {
                OpenProjectFolder();
                return "Abri la carpeta del proyecto.";
            }

            if (LooksLikeCadCommand(prompt))
            {
                SendCadCommand(prompt);
                return "Pase el texto como comando directo a AutoCAD.";
            }

            return "No detecte una intencion segura. Escribe 'ayuda' para ver skills o usa 'cad:' antes de un comando AutoCAD directo.";
        }
        private static string Normalize(string value)
        {
            return value.ToLowerInvariant()
                .Replace("á", "a")
                .Replace("é", "e")
                .Replace("í", "i")
                .Replace("ó", "o")
                .Replace("ú", "u")
                .Replace("ü", "u")
                .Replace("ñ", "n");
        }

        private static bool ContainsAny(string value, params string[] candidates)
        {
            foreach (string candidate in candidates)
            {
                if (value.Contains(candidate))
                {
                    return true;
                }
            }

            return false;
        }

        private static List<double> ExtractNumbers(string value)
        {
            List<double> numbers = new List<double>();
            MatchCollection matches = Regex.Matches(value, @"-?\d+(?:[\.,]\d+)?");
            foreach (Match match in matches)
            {
                string clean = match.Value.Replace(',', '.');
                double number;
                if (double.TryParse(clean, NumberStyles.Float, CultureInfo.InvariantCulture, out number))
                {
                    numbers.Add(number);
                }
            }

            return numbers;
        }

        private static bool LooksLikeCadCommand(string value)
        {
            string trimmed = value.Trim();
            return trimmed.StartsWith("_.") || trimmed.StartsWith("_") || trimmed.StartsWith("-");
        }

        private static bool TryExecuteAgentPlan(string prompt, out string reply)
        {
            reply = string.Empty;
            try
            {
                string script = Path.Combine(ProjectRoot, "autocad_agent", "agent.py");
                if (!File.Exists(script))
                {
                    return false;
                }

                ProcessStartInfo info = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "\"" + script + "\"",
                    WorkingDirectory = ProjectRoot,
                    UseShellExecute = false,
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (Process process = Process.Start(info))
                {
                    if (process == null)
                    {
                        return false;
                    }

                    process.StandardInput.Write(prompt);
                    process.StandardInput.Close();

                    if (!process.WaitForExit(70000))
                    {
                        try
                        {
                            process.Kill();
                        }
                        catch
                        {
                        }

                        reply = "El agente tardo demasiado. Ejecute el fallback local.";
                        return false;
                    }

                    string output = process.StandardOutput.ReadToEnd();
                    string error = process.StandardError.ReadToEnd();
                    if (process.ExitCode != 0 || string.IsNullOrWhiteSpace(output))
                    {
                        reply = "El agente Python fallo: " + error;
                        return false;
                    }

                    JavaScriptSerializer serializer = new JavaScriptSerializer();
                    Dictionary<string, object> plan = serializer.Deserialize<Dictionary<string, object>>(output);
                    object replyValue;
                    reply = plan.TryGetValue("reply", out replyValue) ? Convert.ToString(replyValue) : "Plan ejecutado.";

                    object actionsValue;
                    if (plan.TryGetValue("actions", out actionsValue))
                    {
                        object[] actions = actionsValue as object[];
                        if (actions != null)
                        {
                            foreach (object actionValue in actions)
                            {
                                Dictionary<string, object> action = actionValue as Dictionary<string, object>;
                                if (action != null)
                                {
                                    ExecuteAgentAction(action);
                                }
                            }
                        }
                    }

                    return true;
                }
            }
            catch
            {
                return false;
            }
        }

        private static void ExecuteAgentAction(Dictionary<string, object> action)
        {
            string type = GetString(action, "type", string.Empty);
            switch (type)
            {
                case "create_layers":
                    CreateBaseLayers();
                    break;
                case "architectural_plan":
                    CreateArchitecturalPlan();
                    break;
                case "line":
                    CreateLine(GetDouble(action, "x1", 0), GetDouble(action, "y1", 0), GetDouble(action, "x2", 10), GetDouble(action, "y2", 0), GetString(action, "layer", "TERRENO"));
                    break;
                case "circle":
                    CreateCircle(GetDouble(action, "x", 0), GetDouble(action, "y", 0), GetDouble(action, "radius", 5), GetString(action, "layer", "TERRENO"));
                    break;
                case "rectangle":
                    {
                        double x = GetDouble(action, "x", 0);
                        double y = GetDouble(action, "y", 0);
                        CreateRectangle(x, y, x + GetDouble(action, "width", 10), y + GetDouble(action, "height", 10), GetString(action, "layer", "TERRENO"));
                        break;
                    }
                case "regular_polygon":
                    CreateRegularPolygon((int)GetDouble(action, "sides", 6), GetDouble(action, "radius", 5), GetDouble(action, "x", 0), GetDouble(action, "y", 0), GetString(action, "layer", "TERRENO"));
                    break;
                case "polyline":
                    ExecutePolylineAction(action);
                    break;
                case "text":
                    CreateText(GetString(action, "value", "TEXTO"), GetDouble(action, "x", 0), GetDouble(action, "y", 0), GetDouble(action, "height", 0.6), 0, GetString(action, "layer", "NOTAS"));
                    break;
                case "utm_grid":
                    CreateUtmGrid(GetDouble(action, "spacing", 10));
                    break;
                case "dimension":
                    CreateAlignedDimension(GetDouble(action, "x1", 0), GetDouble(action, "y1", 0), GetDouble(action, "x2", 10), GetDouble(action, "y2", 0));
                    break;
                case "annotate_distances":
                    AnnotateDistances();
                    break;
                case "label_vertices":
                    LabelLastPolylineVertices();
                    break;
                case "move_last":
                    TransformLastEntity(Matrix3d.Displacement(new Vector3d(GetDouble(action, "dx", 0), GetDouble(action, "dy", 0), 0)));
                    break;
                case "copy_last":
                    CopyLastEntity(GetDouble(action, "dx", 0), GetDouble(action, "dy", 0));
                    break;
                case "rotate_last":
                    TransformLastEntity(Matrix3d.Rotation(DegToRad(GetDouble(action, "angle", 0)), Vector3d.ZAxis, new Point3d(GetDouble(action, "cx", 0), GetDouble(action, "cy", 0), 0)));
                    break;
                case "delete_last":
                    DeleteLastEntity();
                    break;
                case "zoom":
                    ZoomExtents();
                    break;
                case "save":
                    SaveDrawing();
                    break;
                case "cad_command":
                    SendCadCommand(GetString(action, "command", string.Empty));
                    break;
            }
        }

        private static void ExecutePolylineAction(Dictionary<string, object> action)
        {
            object pointsValue;
            if (!action.TryGetValue("points", out pointsValue))
            {
                return;
            }

            object[] rawPoints = pointsValue as object[];
            if (rawPoints == null)
            {
                return;
            }

            List<double> numbers = new List<double>();
            foreach (object rawPoint in rawPoints)
            {
                object[] pair = rawPoint as object[];
                if (pair != null && pair.Length >= 2)
                {
                    numbers.Add(Convert.ToDouble(pair[0], CultureInfo.InvariantCulture));
                    numbers.Add(Convert.ToDouble(pair[1], CultureInfo.InvariantCulture));
                }
            }

            if (numbers.Count >= 4)
            {
                CreatePolyline(numbers, GetBool(action, "closed", true), GetString(action, "layer", "TERRENO"));
            }
        }

        private static string GetString(Dictionary<string, object> action, string key, string fallback)
        {
            object value;
            return action.TryGetValue(key, out value) && value != null ? Convert.ToString(value) : fallback;
        }

        private static double GetDouble(Dictionary<string, object> action, string key, double fallback)
        {
            object value;
            if (!action.TryGetValue(key, out value) || value == null)
            {
                return fallback;
            }

            double result;
            return double.TryParse(Convert.ToString(value), NumberStyles.Float, CultureInfo.InvariantCulture, out result) ? result : fallback;
        }

        private static bool GetBool(Dictionary<string, object> action, string key, bool fallback)
        {
            object value;
            if (!action.TryGetValue(key, out value) || value == null)
            {
                return fallback;
            }

            bool result;
            return bool.TryParse(Convert.ToString(value), out result) ? result : fallback;
        }

        private static string ExtractQuotedText(string value)
        {
            Match match = Regex.Match(value, "\"([^\"]+)\"");
            return match.Success ? match.Groups[1].Value : string.Empty;
        }

        private static string TextAfterKeyword(string value, string keyword)
        {
            int index = Normalize(value).IndexOf(keyword);
            if (index < 0)
            {
                return string.Empty;
            }

            string tail = value.Substring(index + keyword.Length).Trim();
            Match number = Regex.Match(tail, @"-?\d");
            if (number.Success)
            {
                tail = tail.Substring(0, number.Index).Trim();
            }

            return tail.Trim(':', '-', ' ');
        }

        private static double DegToRad(double degrees)
        {
            return Math.PI * degrees / 180.0;
        }

        private static int ExtractIntAfter(string normalized, string keyword, int fallback)
        {
            Match match = Regex.Match(normalized, @"(\d+)\s*" + Regex.Escape(keyword));
            if (!match.Success)
            {
                match = Regex.Match(normalized, Regex.Escape(keyword) + @"\s*(\d+)");
            }

            int value;
            return match.Success && int.TryParse(match.Groups[1].Value, out value) ? value : fallback;
        }

        private static double ExtractDoubleAfter(string normalized, string keyword, double fallback)
        {
            Match match = Regex.Match(normalized, Regex.Escape(keyword) + @"\s*(-?\d+(?:[\.,]\d+)?)");
            if (!match.Success)
            {
                return fallback;
            }

            double value;
            return double.TryParse(
                match.Groups[1].Value.Replace(',', '.'),
                NumberStyles.Float,
                CultureInfo.InvariantCulture,
                out value)
                ? value
                : fallback;
        }

        private static Point2d ExtractOrigin(string prompt, List<double> numbers, int fallbackIndex)
        {
            string normalized = Normalize(prompt);
            Match match = Regex.Match(normalized, @"(?:origen|desde|en)\s*(-?\d+(?:[\.,]\d+)?)\s*[, ]\s*(-?\d+(?:[\.,]\d+)?)");
            if (match.Success)
            {
                double x;
                double y;
                if (double.TryParse(match.Groups[1].Value.Replace(',', '.'), NumberStyles.Float, CultureInfo.InvariantCulture, out x)
                    && double.TryParse(match.Groups[2].Value.Replace(',', '.'), NumberStyles.Float, CultureInfo.InvariantCulture, out y))
                {
                    return new Point2d(x, y);
                }
            }

            if (numbers.Count >= fallbackIndex + 2)
            {
                return new Point2d(numbers[fallbackIndex], numbers[fallbackIndex + 1]);
            }

            return new Point2d(0, 0);
        }

        private static void SendCadCommand(string command)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                if (!command.EndsWith(" "))
                {
                    command += " ";
                }

                doc.SendStringToExecute(command, true, false, false);
            }
        }

        private static void SaveDrawing()
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                doc.Database.SaveAs(doc.Database.Filename, true, DwgVersion.Current, doc.Database.SecurityParameters);
            }
        }

        private static void CreateLine(double x1, double y1, double x2, double y2, string layer)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureLayer(doc.Database, tr, layer, 3);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                AppendLine(modelSpace, tr, x1, y1, x2, y2, layer);
                tr.Commit();
            }
        }

        private static void CreateCircle(double x, double y, double radius, string layer)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureLayer(doc.Database, tr, layer, 3);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                Circle circle = new Circle(new Point3d(x, y, 0), Vector3d.ZAxis, radius)
                {
                    Layer = layer
                };
                modelSpace.AppendEntity(circle);
                tr.AddNewlyCreatedDBObject(circle, true);
                tr.Commit();
            }
        }

        private static void CreateArchitecturalPlan()
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureArchitecturalLayers(doc.Database, tr);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);

                // Muros exteriores e interiores en metros. Espesor base 0.15 m.
                AppendRect(modelSpace, tr, 0, 0, 10, 8, "ARQ-MUROS");
                AppendRect(modelSpace, tr, 0.15, 0.15, 9.85, 7.85, "ARQ-MUROS");
                AppendWall(modelSpace, tr, 0.15, 4.6, 9.85, 4.75);
                AppendWall(modelSpace, tr, 3.5, 0.15, 3.65, 4.6);
                AppendWall(modelSpace, tr, 6.6, 0.15, 6.75, 4.6);
                AppendWall(modelSpace, tr, 6.6, 2.2, 9.85, 2.35);

                // Vanos/puertas y ventanas simbolicos.
                AppendDoor(modelSpace, tr, 1.0, 0.15, 1.9, 0.15, true);
                AppendDoor(modelSpace, tr, 3.65, 2.0, 3.65, 2.85, false);
                AppendDoor(modelSpace, tr, 6.6, 2.8, 6.6, 3.65, true);
                AppendDoor(modelSpace, tr, 7.6, 4.6, 8.45, 4.6, true);
                AppendWindow(modelSpace, tr, 4.4, 7.85, 6.0, 7.85);
                AppendWindow(modelSpace, tr, 8.0, 7.85, 9.3, 7.85);
                AppendWindow(modelSpace, tr, 0.15, 5.4, 0.15, 7.0);
                AppendWindow(modelSpace, tr, 4.2, 0.15, 5.7, 0.15);

                // Mobiliario simple para lectura.
                AppendRect(modelSpace, tr, 0.7, 5.25, 3.0, 6.05, "ARQ-MOBILIARIO");
                AppendRect(modelSpace, tr, 4.15, 1.0, 5.85, 2.25, "ARQ-MOBILIARIO");
                AppendRect(modelSpace, tr, 7.2, 1.0, 9.25, 2.0, "ARQ-MOBILIARIO");
                AppendRect(modelSpace, tr, 7.1, 2.75, 9.3, 3.8, "ARQ-MOBILIARIO");
                AppendCircle(modelSpace, tr, 8.15, 3.25, 0.22, "ARQ-MOBILIARIO");

                // Etiquetas de espacios.
                AppendText(modelSpace, tr, "SALA-COMEDOR", 1.0, 6.4, 0.25, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "COCINA", 7.4, 6.4, 0.25, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "RECAMARA 1", 0.9, 2.4, 0.25, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "RECAMARA 2", 4.4, 2.4, 0.25, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "BANO", 7.6, 3.25, 0.22, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "PATIO / SERVICIO", 7.1, 1.05, 0.22, 0, "ARQ-TEXTOS");

                // Cotas generales.
                AppendDimension(modelSpace, tr, doc.Database, 0, -0.65, 10, -0.65, 0, -1.05);
                AppendDimension(modelSpace, tr, doc.Database, -0.65, 0, -0.65, 8, -1.05, 0);
                AppendText(modelSpace, tr, "PLANTA ARQUITECTONICA HABITACIONAL", 0, 8.65, 0.32, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "ESCALA SUGERIDA 1:50 | UNIDADES: METROS", 0, 8.25, 0.22, 0, "ARQ-TEXTOS");

                // Norte y notas normativas.
                AppendLine(modelSpace, tr, 11.2, 6.2, 11.2, 7.4, "ARQ-EJES");
                AppendLine(modelSpace, tr, 11.2, 7.4, 10.95, 7.05, "ARQ-EJES");
                AppendLine(modelSpace, tr, 11.2, 7.4, 11.45, 7.05, "ARQ-EJES");
                AppendText(modelSpace, tr, "N", 11.05, 7.55, 0.3, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "NOTAS NORMATIVAS:", 11.0, 5.3, 0.22, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "1. Verificar reglamento local antes de construir.", 11.0, 4.95, 0.18, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "2. Muros base 0.15 m; ajustar por calculo estructural.", 11.0, 4.65, 0.18, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "3. Puertas minimas sugeridas 0.80-0.90 m.", 11.0, 4.35, 0.18, 0, "ARQ-TEXTOS");
                AppendText(modelSpace, tr, "4. Ventilacion/iluminacion natural segun norma local.", 11.0, 4.05, 0.18, 0, "ARQ-TEXTOS");

                tr.Commit();
            }

            ZoomExtents();
        }

        private static void CreateRectangle(double x1, double y1, double x2, double y2, string layer)
        {
            List<double> numbers = new List<double>
            {
                x1, y1,
                x2, y1,
                x2, y2,
                x1, y2
            };
            CreatePolyline(numbers, true, layer);
        }

        private static void CreatePolyline(List<double> numbers, bool closed, string layer)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureLayer(doc.Database, tr, layer, 3);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                Polyline polyline = new Polyline();
                for (int i = 0; i < numbers.Count; i += 2)
                {
                    polyline.AddVertexAt(i / 2, new Point2d(numbers[i], numbers[i + 1]), 0, 0, 0);
                }

                polyline.Closed = closed;
                polyline.Layer = layer;
                modelSpace.AppendEntity(polyline);
                tr.AddNewlyCreatedDBObject(polyline, true);
                tr.Commit();
            }
        }

        private static void CreateRegularPolygon(int sides, double radius, double originX, double originY, string layer)
        {
            List<double> numbers = new List<double>();
            double startAngle = Math.PI / 2.0;
            for (int i = 0; i < sides; i++)
            {
                double angle = startAngle + (2.0 * Math.PI * i / sides);
                numbers.Add(originX + Math.Cos(angle) * radius);
                numbers.Add(originY + Math.Sin(angle) * radius);
            }

            CreatePolyline(numbers, true, layer);
        }

        private static void CreateText(string value, double x, double y, double height, double rotation, string layer)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureLayer(doc.Database, tr, layer, 6);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                AppendText(modelSpace, tr, value, x, y, height, DegToRad(rotation), layer);
                tr.Commit();
            }
        }

        private static void CreateAlignedDimension(double x1, double y1, double x2, double y2)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureLayer(doc.Database, tr, "ANOTACIONES", 2);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                Point3d p1 = new Point3d(x1, y1, 0);
                Point3d p2 = new Point3d(x2, y2, 0);
                Point3d dimPoint = new Point3d((x1 + x2) / 2.0, (y1 + y2) / 2.0 + 1.0, 0);
                AlignedDimension dimension = new AlignedDimension(p1, p2, dimPoint, string.Empty, doc.Database.Dimstyle)
                {
                    Layer = "ANOTACIONES"
                };
                modelSpace.AppendEntity(dimension);
                tr.AddNewlyCreatedDBObject(dimension, true);
                tr.Commit();
            }
        }

        private static void AnnotateDistances()
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureLayer(doc.Database, tr, "ANOTACIONES", 2);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                ObjectId[] ids = modelSpace.Cast<ObjectId>().ToArray();
                foreach (ObjectId id in ids)
                {
                    Line line = tr.GetObject(id, OpenMode.ForRead) as Line;
                    if (line == null)
                    {
                        continue;
                    }

                    double length = line.StartPoint.DistanceTo(line.EndPoint);
                    Point3d mid = new Point3d(
                        (line.StartPoint.X + line.EndPoint.X) / 2.0,
                        (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
                        0);
                    AppendText(modelSpace, tr, length.ToString("0.##"), mid.X, mid.Y, 0.6, 0, "ANOTACIONES");
                }

                tr.Commit();
            }
        }

        private static void LabelLastPolylineVertices()
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                EnsureLayer(doc.Database, tr, "VERTICES", 1);
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                Polyline polyline = GetLastEntity(tr, modelSpace) as Polyline;
                if (polyline == null)
                {
                    throw new InvalidOperationException("La ultima entidad no es polilinea.");
                }

                for (int i = 0; i < polyline.NumberOfVertices; i++)
                {
                    Point2d point = polyline.GetPoint2dAt(i);
                    AppendText(modelSpace, tr, "V" + (i + 1), point.X, point.Y, 0.6, 0, "VERTICES");
                }

                tr.Commit();
            }
        }

        private static void DeleteLastEntity()
        {
            WithLastEntity(delegate(Entity entity)
            {
                entity.Erase();
            });
        }

        private static void TransformLastEntity(Matrix3d transform)
        {
            WithLastEntity(delegate(Entity entity)
            {
                entity.TransformBy(transform);
            });
        }

        private static void CopyLastEntity(double dx, double dy)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                Entity last = GetLastEntity(tr, modelSpace);
                Entity copy = (Entity)last.Clone();
                copy.TransformBy(Matrix3d.Displacement(new Vector3d(dx, dy, 0)));
                modelSpace.AppendEntity(copy);
                tr.AddNewlyCreatedDBObject(copy, true);
                tr.Commit();
            }
        }

        private static void WithLastEntity(Action<Entity> action)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return;
            }

            using (doc.LockDocument())
            using (Transaction tr = doc.Database.TransactionManager.StartTransaction())
            {
                BlockTable blockTable = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                BlockTableRecord modelSpace =
                    (BlockTableRecord)tr.GetObject(blockTable[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                Entity entity = GetLastEntity(tr, modelSpace);
                if (!entity.IsWriteEnabled)
                {
                    entity.UpgradeOpen();
                }

                action(entity);
                tr.Commit();
            }
        }

        private static Entity GetLastEntity(Transaction tr, BlockTableRecord modelSpace)
        {
            ObjectId lastId = ObjectId.Null;
            foreach (ObjectId id in modelSpace)
            {
                lastId = id;
            }

            if (lastId == ObjectId.Null)
            {
                throw new InvalidOperationException("No hay entidades en Model Space.");
            }

            return (Entity)tr.GetObject(lastId, OpenMode.ForWrite);
        }

        private static void CopyMcpCommand()
        {
            string command = string.Format("cd /d \"{0}\" && python -m autocad_mcp.server", ProjectRoot);
            Clipboard.SetText(command);
            WriteMessage("\nComando MCP copiado al portapapeles.");
        }

        private static void OpenProjectFolder()
        {
            if (Directory.Exists(ProjectRoot))
            {
                Process.Start("explorer.exe", ProjectRoot);
            }
        }

        private static void ShowHelp()
        {
            WriteMessage("\nCarga la DLL con NETLOAD. Abre la paleta con CODEXPAL.");
        }

        private static void EnsureLayer(Database db, Transaction tr, string name, short colorIndex)
        {
            LayerTable layerTable = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForRead);
            if (!layerTable.Has(name))
            {
                layerTable.UpgradeOpen();
                using (LayerTableRecord layer = new LayerTableRecord())
                {
                    layer.Name = name;
                    layer.Color = AcadColor.FromColorIndex(ColorMethod.ByAci, colorIndex);
                    layerTable.Add(layer);
                    tr.AddNewlyCreatedDBObject(layer, true);
                }
            }
        }

        private static void EnsureArchitecturalLayers(Database db, Transaction tr)
        {
            EnsureLayer(db, tr, "ARQ-MUROS", 7);
            EnsureLayer(db, tr, "ARQ-PUERTAS", 3);
            EnsureLayer(db, tr, "ARQ-VENTANAS", 4);
            EnsureLayer(db, tr, "ARQ-MOBILIARIO", 8);
            EnsureLayer(db, tr, "ARQ-COTAS", 2);
            EnsureLayer(db, tr, "ARQ-TEXTOS", 6);
            EnsureLayer(db, tr, "ARQ-EJES", 1);
        }

        private static Extents3d GetDrawableExtents(Database db)
        {
            try
            {
                return new Extents3d(db.Extmin, db.Extmax);
            }
            catch
            {
                return new Extents3d(new Point3d(0, 0, 0), new Point3d(100, 100, 0));
            }
        }

        private static void AppendLine(
            BlockTableRecord modelSpace,
            Transaction tr,
            double x1,
            double y1,
            double x2,
            double y2,
            string layer)
        {
            Line line = new Line(new Point3d(x1, y1, 0), new Point3d(x2, y2, 0))
            {
                Layer = layer
            };
            modelSpace.AppendEntity(line);
            tr.AddNewlyCreatedDBObject(line, true);
        }

        private static void AppendRect(
            BlockTableRecord modelSpace,
            Transaction tr,
            double x1,
            double y1,
            double x2,
            double y2,
            string layer)
        {
            Polyline rect = new Polyline();
            rect.AddVertexAt(0, new Point2d(x1, y1), 0, 0, 0);
            rect.AddVertexAt(1, new Point2d(x2, y1), 0, 0, 0);
            rect.AddVertexAt(2, new Point2d(x2, y2), 0, 0, 0);
            rect.AddVertexAt(3, new Point2d(x1, y2), 0, 0, 0);
            rect.Closed = true;
            rect.Layer = layer;
            modelSpace.AppendEntity(rect);
            tr.AddNewlyCreatedDBObject(rect, true);
        }

        private static void AppendWall(
            BlockTableRecord modelSpace,
            Transaction tr,
            double x1,
            double y1,
            double x2,
            double y2)
        {
            AppendRect(modelSpace, tr, x1, y1, x2, y2, "ARQ-MUROS");
        }

        private static void AppendDoor(
            BlockTableRecord modelSpace,
            Transaction tr,
            double x1,
            double y1,
            double x2,
            double y2,
            bool swingUp)
        {
            AppendLine(modelSpace, tr, x1, y1, x2, y2, "ARQ-PUERTAS");
            double radius = Math.Sqrt(Math.Pow(x2 - x1, 2) + Math.Pow(y2 - y1, 2));
            Arc arc = new Arc(
                new Point3d(x1, y1, 0),
                radius,
                swingUp ? 0 : -Math.PI / 2.0,
                swingUp ? Math.PI / 2.0 : 0)
            {
                Layer = "ARQ-PUERTAS"
            };
            modelSpace.AppendEntity(arc);
            tr.AddNewlyCreatedDBObject(arc, true);
        }

        private static void AppendWindow(
            BlockTableRecord modelSpace,
            Transaction tr,
            double x1,
            double y1,
            double x2,
            double y2)
        {
            AppendLine(modelSpace, tr, x1, y1, x2, y2, "ARQ-VENTANAS");
            if (Math.Abs(y1 - y2) < 0.001)
            {
                AppendLine(modelSpace, tr, x1, y1 + 0.05, x2, y2 + 0.05, "ARQ-VENTANAS");
                AppendLine(modelSpace, tr, x1, y1 - 0.05, x2, y2 - 0.05, "ARQ-VENTANAS");
            }
            else
            {
                AppendLine(modelSpace, tr, x1 + 0.05, y1, x2 + 0.05, y2, "ARQ-VENTANAS");
                AppendLine(modelSpace, tr, x1 - 0.05, y1, x2 - 0.05, y2, "ARQ-VENTANAS");
            }
        }

        private static void AppendCircle(
            BlockTableRecord modelSpace,
            Transaction tr,
            double x,
            double y,
            double radius,
            string layer)
        {
            Circle circle = new Circle(new Point3d(x, y, 0), Vector3d.ZAxis, radius)
            {
                Layer = layer
            };
            modelSpace.AppendEntity(circle);
            tr.AddNewlyCreatedDBObject(circle, true);
        }

        private static void AppendDimension(
            BlockTableRecord modelSpace,
            Transaction tr,
            Database db,
            double x1,
            double y1,
            double x2,
            double y2,
            double dimX,
            double dimY)
        {
            AlignedDimension dimension = new AlignedDimension(
                new Point3d(x1, y1, 0),
                new Point3d(x2, y2, 0),
                new Point3d(dimX, dimY, 0),
                string.Empty,
                db.Dimstyle)
            {
                Layer = "ARQ-COTAS"
            };
            modelSpace.AppendEntity(dimension);
            tr.AddNewlyCreatedDBObject(dimension, true);
        }

        private static void AppendText(
            BlockTableRecord modelSpace,
            Transaction tr,
            string value,
            double x,
            double y,
            double height,
            double rotation)
        {
            DBText text = new DBText
            {
                TextString = value,
                Position = new Point3d(x, y, 0),
                Height = height,
                Rotation = rotation,
                Layer = "RETICULA"
            };
            modelSpace.AppendEntity(text);
            tr.AddNewlyCreatedDBObject(text, true);
        }

        private static void AppendText(
            BlockTableRecord modelSpace,
            Transaction tr,
            string value,
            double x,
            double y,
            double height,
            double rotation,
            string layer)
        {
            DBText text = new DBText
            {
                TextString = value,
                Position = new Point3d(x, y, 0),
                Height = height,
                Rotation = rotation,
                Layer = layer
            };
            modelSpace.AppendEntity(text);
            tr.AddNewlyCreatedDBObject(text, true);
        }

        private static void WriteMessage(string message)
        {
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                doc.Editor.WriteMessage(message);
            }
        }
    }
}
