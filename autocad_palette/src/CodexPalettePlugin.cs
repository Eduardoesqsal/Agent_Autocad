using System;
using System.Drawing;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.Windows;

namespace CodexAutoCADPalette
{
    public sealed class CodexPalettePlugin : IExtensionApplication
    {
        private static readonly Guid PaletteGuid = new Guid("F54B76CB-4B89-4C3B-A1E1-6732BD771E42");
        private static PaletteSet palette;

        public void Initialize()
        {
            ShowPalette();
        }

        public void Terminate()
        {
        }

        [CommandMethod("CODEXPAL", CommandFlags.Session)]
        [CommandMethod("CODEXPALETA", CommandFlags.Session)]
        [CommandMethod("PALETACODEX", CommandFlags.Session)]
        [CommandMethod("CODEXCHAT", CommandFlags.Session)]
        public static void ShowPaletteCommand()
        {
            ShowPalette();
        }

        [CommandMethod("CODEXCAPAS", CommandFlags.Session)]
        public static void CreateLayersCommand()
        {
            CodexPaletteControl.CreateBaseLayers();
        }

        [CommandMethod("CODEXRETICULA", CommandFlags.Session)]
        public static void CreateGridCommand()
        {
            CodexPaletteControl.CreateUtmGrid();
        }

        private static void ShowPalette()
        {
            if (palette == null)
            {
                palette = new PaletteSet("Codex AutoCAD MCP", PaletteGuid)
                {
                    Style =
                        PaletteSetStyles.ShowAutoHideButton
                        | PaletteSetStyles.ShowCloseButton
                        | PaletteSetStyles.ShowPropertiesMenu,
                    DockEnabled = DockSides.Left | DockSides.Right,
                    MinimumSize = new Size(320, 460),
                    Size = new Size(360, 620)
                };

                palette.Add("Codex", new CodexPaletteControl());
            }

            palette.Visible = true;
            palette.Activate(0);
        }
    }
}
