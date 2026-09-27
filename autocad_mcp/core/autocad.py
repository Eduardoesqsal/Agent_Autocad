from __future__ import annotations

import logging
import math
import os
import re
import subprocess
import time
import winreg
from typing import Any, ClassVar

import pythoncom
from pywintypes import com_error as COMError
from win32com.client import VARIANT, GetActiveObject

from autocad_mcp.core.language import translate_cmd
from autocad_mcp.models import Point2D

logger = logging.getLogger(__name__)


AUTOCAD_PROG_IDS = ("AutoCAD.Application", "AutoCAD.Application.24")
AUTOCAD_CLSIDS = ("{8B4929F8-076F-4AEC-AFEE-8928747B7AE3}",)
AUTOCAD_CLSID = AUTOCAD_CLSIDS[0]
AUTOCAD_EXE_CANDIDATES = (
    os.environ.get("AUTOCAD_EXE", ""),
    r"C:\Program Files\Autodesk\AutoCAD 2021\acad.exe",
    r"C:\Program Files (x86)\Autodesk\AutoCAD 2021\acad.exe",
)
AUTOCAD_AUTOLAUNCH_DEFAULT = os.environ.get(
    "AUTOCAD_AUTOLAUNCH", "1"
).strip().lower() in {"1", "true", "yes", "si"}
AUTOCAD_WAIT_TIMEOUT = float(os.environ.get("AUTOCAD_WAIT_TIMEOUT", "300"))
AUTOCAD_WAIT_INTERVAL = float(os.environ.get("AUTOCAD_WAIT_INTERVAL", "2"))
DEFAULT_TEXT_HEIGHT = 2.5
BLOQUES_LIBRARY_PATH = r"C:\Users\eduar\Downloads\141088v6007075_mobiliariosdinamicosparaviviendas\Mobiliario Dinamico.dwg"


class AutoCADError(RuntimeError):
    pass


class AutoCADConnection:
    _instance: AutoCADConnection | None = None

    def __init__(self) -> None:
        self._app: Any = None
        self._doc: Any = None

    @classmethod
    def get_instance(cls) -> AutoCADConnection:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def _buscar_autocad_exe() -> str | None:
        for candidato in AUTOCAD_EXE_CANDIDATES:
            if candidato and os.path.isfile(candidato):
                return candidato
        return None

    @staticmethod
    def _obtener_localserver32() -> str | None:
        clave = rf"CLSID\\{AUTOCAD_CLSID}\\LocalServer32"
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, clave) as handle:
                valor, _ = winreg.QueryValueEx(handle, "")
        except OSError:
            return None
        valor = str(valor).strip()
        return valor or None

    @staticmethod
    def _abrir_autocad_automatizado() -> str | None:
        comando = AutoCADConnection._obtener_localserver32()
        if comando:
            partes = comando.split()
            ejecutable = partes[0].strip('"')
            argumentos = partes[1:] if len(partes) > 1 else ["/Automation"]
            try:
                subprocess.Popen(
                    [ejecutable, *argumentos],
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                return comando
            except (OSError, FileNotFoundError):
                return None
        ruta = AutoCADConnection._buscar_autocad_exe()
        if ruta is None:
            return None
        try:
            subprocess.Popen(
                [ruta, "/Automation"],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, FileNotFoundError):
            return None
        return ruta

    @staticmethod
    def _esperar_com_autocad(
        timeout_s: float = AUTOCAD_WAIT_TIMEOUT,
        intervalo_s: float = AUTOCAD_WAIT_INTERVAL,
    ) -> Any:
        deadline = time.monotonic() + float(timeout_s)
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            for candidate in (*AUTOCAD_PROG_IDS, *AUTOCAD_CLSIDS):
                try:
                    return GetActiveObject(candidate)
                except (COMError, OSError) as exc:
                    last_error = exc
            time.sleep(float(intervalo_s))
        raise AutoCADError(
            "AutoCAD no expuso COM dentro del tiempo de espera."
        ) from last_error

    def connect(self, *, autolaunch: bool | None = None) -> None:
        pythoncom.CoInitialize()
        if autolaunch is None:
            autolaunch = AUTOCAD_AUTOLAUNCH_DEFAULT
        for candidate in (*AUTOCAD_PROG_IDS, *AUTOCAD_CLSIDS):
            try:
                self._app = GetActiveObject(candidate)
                break
            except (COMError, OSError):
                logger.debug("AutoCAD COM candidate not available: %s", candidate)
        else:
            if autolaunch:
                self._abrir_autocad_automatizado()
                try:
                    self._app = self._esperar_com_autocad()
                except AutoCADError:
                    pass
            if self._app is None:
                self._app = self._esperar_com_autocad()
        try:
            self._doc = self._app.ActiveDocument
        except (COMError, AttributeError, TypeError) as exc:
            raise AutoCADError("No hay un documento activo en AutoCAD.") from exc

    @property
    def app(self) -> Any:
        if self._app is None:
            self.connect()
        return self._app

    @property
    def doc(self) -> Any:
        if self._doc is None:
            self.connect()
        return self._doc

    @property
    def model_space(self) -> Any:
        return self.doc.ModelSpace

    def send_command(self, cmd: str, translate: bool = True) -> None:
        if translate:
            parts = cmd.strip().split(None, 1)
            if parts:
                translated_cmd = translate_cmd(parts[0])
                if len(parts) > 1:
                    cmd = f"{translated_cmd} {parts[1]}"
                else:
                    cmd = translated_cmd
        if not cmd.endswith(" ") and not cmd.endswith("\n"):
            cmd += " "
        self.doc.SendCommand(cmd)

    def refresh_document(self) -> None:
        try:
            self._doc = self._app.ActiveDocument
        except (AttributeError, TypeError):
            logger.debug("Attribute not available on entity")

    def _point_array(self, x: float, y: float, z: float = 0.0) -> VARIANT:
        return VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (float(x), float(y), float(z))
        )

    def _flat_coords(self, points: list[Point2D]) -> VARIANT:
        coords: list[float] = []
        for point in points:
            coords.extend([float(point.x), float(point.y)])
        return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, tuple(coords))

    def _safe_set(self, obj: Any, attr: str, value: Any) -> None:
        try:
            setattr(obj, attr, value)
        except (AttributeError, TypeError):
            logger.debug("Attribute not available on entity")

    def add_line(
        self, x1: float, y1: float, x2: float, y2: float, layer: str | None = None
    ) -> dict[str, Any]:
        entidad = self.model_space.AddLine(
            self._point_array(x1, y1), self._point_array(x2, y2)
        )
        self._apply_layer(entidad, layer)
        return {
            "tipo": "Linea",
            "handle": str(getattr(entidad, "Handle", "")),
            "layer": layer or "",
        }

    def add_circle(
        self, x: float, y: float, radio: float, layer: str | None = None
    ) -> dict[str, Any]:
        if float(radio) <= 0:
            raise AutoCADError("El radio debe ser mayor que cero.")
        entidad = self.model_space.AddCircle(self._point_array(x, y), float(radio))
        self._apply_layer(entidad, layer)
        return {
            "tipo": "Circulo",
            "handle": str(getattr(entidad, "Handle", "")),
            "layer": layer or "",
        }

    def add_polyline(
        self, puntos: list[Point2D], cerrar: bool = False, layer: str | None = None
    ) -> dict[str, Any]:
        if len(puntos) < 2:
            raise AutoCADError("La polilinea requiere al menos dos puntos.")
        coords = self._flat_coords(puntos)
        entidad = self.model_space.AddLightWeightPolyline(coords)
        if cerrar:
            entidad.Closed = True
        self._apply_layer(entidad, layer)
        return {
            "tipo": "Polilinea",
            "handle": str(getattr(entidad, "Handle", "")),
            "puntos": len(puntos),
            "cerrada": bool(cerrar),
            "layer": layer or "",
        }

    def add_rectangle(
        self, x1: float, y1: float, x2: float, y2: float, layer: str | None = None
    ) -> dict[str, Any]:
        min_x, max_x = float(min(x1, x2)), float(max(x1, x2))
        min_y, max_y = float(min(y1, y2)), float(max(y1, y2))
        puntos = [
            Point2D(min_x, min_y),
            Point2D(max_x, min_y),
            Point2D(max_x, max_y),
            Point2D(min_x, max_y),
            Point2D(min_x, min_y),
        ]
        return self.add_polyline(puntos, cerrar=True, layer=layer)

    def add_text(
        self,
        texto: str,
        x: float,
        y: float,
        altura: float = DEFAULT_TEXT_HEIGHT,
        layer: str | None = None,
        rotacion: float = 0.0,
    ) -> dict[str, Any]:
        entidad = self.model_space.AddText(
            str(texto), self._point_array(x, y), float(altura)
        )
        if float(rotacion) != 0.0:
            self._safe_set(entidad, "Rotation", math.radians(float(rotacion)))
        self._apply_layer(entidad, layer)
        return {
            "tipo": "Texto",
            "handle": str(getattr(entidad, "Handle", "")),
            "texto": str(texto),
            "layer": layer or "",
            "rotacion": float(rotacion),
        }

    def add_arc(
        self,
        x: float,
        y: float,
        radio: float,
        angulo_inicio: float,
        angulo_fin: float,
        layer: str | None = None,
    ) -> dict[str, Any]:
        entidad = self.model_space.AddArc(
            self._point_array(x, y),
            float(radio),
            math.radians(float(angulo_inicio)),
            math.radians(float(angulo_fin)),
        )
        self._apply_layer(entidad, layer)
        return {
            "tipo": "Arco",
            "handle": str(getattr(entidad, "Handle", "")),
            "layer": layer or "",
        }

    def insert_block(
        self,
        nombre: str,
        x: float,
        y: float,
        escala: float = 1.0,
        rotacion: float = 0.0,
        layer: str | None = None,
    ) -> dict[str, Any]:
        try:
            entidad = self.model_space.InsertBlock(
                self._point_array(x, y),
                str(nombre),
                float(escala),
                float(escala),
                float(escala),
                math.radians(float(rotacion)),
            )
        except (COMError, RuntimeError):
            self._importar_bloque_libreria(nombre)
            try:
                entidad = self.model_space.InsertBlock(
                    self._point_array(x, y),
                    str(nombre),
                    float(escala),
                    float(escala),
                    float(escala),
                    math.radians(float(rotacion)),
                )
            except (COMError, RuntimeError) as exc2:
                return {
                    "tipo": "Bloque",
                    "handle": "",
                    "nombre": nombre,
                    "layer": layer or "",
                    "insertado": False,
                    "error": str(exc2),
                }
        self._apply_layer(entidad, layer)
        return {
            "tipo": "Bloque",
            "handle": str(getattr(entidad, "Handle", "")),
            "nombre": str(nombre),
            "x": float(x),
            "y": float(y),
            "layer": layer or "",
            "insertado": True,
        }

    def _importar_bloque_libreria(self, nombre: str) -> bool:
        try:
            cmd = f'_.-INSERT "{BLOQUES_LIBRARY_PATH}|{nombre}" 9999,9999 1 1 0 '
            self.send_command(cmd, translate=False)
            time.sleep(0.2)
            return True
        except (OSError, RuntimeError):
            return False

    def _apply_layer(self, entity: Any, layer: str | None) -> None:
        if layer:
            self._safe_set(entity, "Layer", layer)

    def zoom_extents(self) -> None:
        try:
            self.send_command("_.ZOOM _E", translate=False)
        except (AttributeError, TypeError):
            logger.debug("Attribute not available on entity")

    def save_dwg(self) -> dict[str, Any]:
        self.doc.Save()
        return {"guardado": True, "archivo": str(getattr(self.doc, "FullName", ""))}

    def count_entities(self) -> dict[str, Any]:
        ms = int(getattr(self.model_space, "Count", 0))
        ps = (
            int(getattr(self.doc.PaperSpace, "Count", 0))
            if getattr(self.doc, "PaperSpace", None)
            else 0
        )
        return {"model_space": ms, "paper_space": ps, "total": ms + ps}

    def get_active_drawing_info(self) -> dict[str, Any]:
        layout = getattr(getattr(self.doc, "ActiveLayout", None), "Name", "")
        return {
            "nombre": str(getattr(self.doc, "Name", "")),
            "archivo": str(getattr(self.doc, "FullName", "")),
            "ruta": str(getattr(self.doc, "Path", "")),
            "layout_activo": str(layout),
            "guardado": bool(str(getattr(self.doc, "FullName", ""))),
        }

    def load_linetype(self, nombre: str, archivo: str = "acad.lin") -> dict[str, Any]:
        try:
            for lt in self._iter_collection_items(self.doc.Linetypes):
                if str(getattr(lt, "Name", "")).lower() == nombre.lower():
                    return {
                        "cargado": True,
                        "nombre": nombre,
                        "ya_existia": True,
                        "error": None,
                    }
            self.doc.Linetypes.Load(nombre, archivo)
            return {
                "cargado": True,
                "nombre": nombre,
                "ya_existia": False,
                "error": None,
            }
        except (COMError, RuntimeError) as exc:
            return {
                "cargado": False,
                "nombre": nombre,
                "ya_existia": False,
                "error": str(exc),
            }

    def list_layers(self) -> list[dict[str, Any]]:
        capas: list[dict[str, Any]] = []
        for capa in self._iter_collection_items(self.doc.Layers):
            capas.append(
                {
                    "nombre": str(getattr(capa, "Name", "")),
                    "color": int(getattr(capa, "Color", 0)),
                    "linetype": str(getattr(capa, "Linetype", "")),
                    "activa": bool(getattr(capa, "On", True)),
                    "congelada": bool(getattr(capa, "Freeze", False)),
                    "bloqueada": bool(getattr(capa, "Lock", False)),
                }
            )
        return capas

    def find_layer(self, nombre: str) -> Any | None:
        try:
            return self.doc.Layers.Item(nombre)
        except (AttributeError, TypeError):
            for capa in self._iter_collection_items(self.doc.Layers):
                if str(getattr(capa, "Name", "")).lower() == nombre.lower():
                    return capa
        return None

    def ensure_layer(
        self,
        nombre: str,
        *,
        color: int | None = None,
        linetype: str | None = None,
        lineweight: int | None = None,
    ) -> dict[str, Any]:
        clean_name = str(nombre).strip()
        if not clean_name:
            raise AutoCADError("El nombre de la capa no puede estar vacio.")
        capa = self.find_layer(clean_name)
        creada = False
        if capa is None:
            capa = self.doc.Layers.Add(clean_name)
            creada = True
        if color is not None:
            self._safe_set(capa, "Color", int(color))
        if linetype is not None:
            self.load_linetype(linetype)
            self._safe_set(capa, "Linetype", str(linetype))
        if lineweight is not None:
            self._safe_set(capa, "Lineweight", int(lineweight))
        return {
            "creada": creada,
            "nombre": str(getattr(capa, "Name", clean_name)),
            "color": int(getattr(capa, "Color", color or 0)),
            "linetype": str(getattr(capa, "Linetype", linetype or "")),
            "lineweight": int(getattr(capa, "Lineweight", lineweight or 0)),
        }

    def list_blocks(self) -> list[dict[str, Any]]:
        bloques: list[dict[str, Any]] = []
        for bloque in self._iter_collection_items(self.doc.Blocks):
            bloques.append(
                {
                    "nombre": str(getattr(bloque, "Name", "")),
                    "is_layout": bool(getattr(bloque, "IsLayout", False)),
                    "is_xref": bool(getattr(bloque, "IsXRef", False)),
                    "cantidad": int(getattr(bloque, "Count", 0)),
                }
            )
        return bloques

    @staticmethod
    def _iter_collection_items(collection: Any) -> list[Any]:
        count = int(getattr(collection, "Count", 0))
        items: list[Any] = []
        for indice in range(count):
            item = None
            for key in (indice, indice + 1):
                try:
                    item = collection.Item(key)
                    break
                except (AttributeError, TypeError):
                    logger.debug("Could not access collection item")
            if item is not None:
                items.append(item)
        return items

    @staticmethod
    def _text_center(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    @staticmethod
    def diagnosticar() -> dict[str, Any]:
        pythoncom.CoInitialize()
        proceso_count = 0
        try:
            salida = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-Process acad -ErrorAction SilentlyContinue | Measure-Object).Count",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            proceso_count = int(salida or "0")
        except (OSError, subprocess.SubprocessError):
            proceso_count = 0
        candidatos = []
        for candidate in (*AUTOCAD_PROG_IDS, *AUTOCAD_CLSIDS):
            try:
                app = GetActiveObject(candidate)
                doc_name = str(getattr(app.ActiveDocument, "Name", "")) if app else ""
                candidatos.append(
                    {
                        "candidato": candidate,
                        "disponible": True,
                        "documento_activo": doc_name,
                    }
                )
            except (COMError, OSError) as exc:
                candidatos.append(
                    {"candidato": candidate, "disponible": False, "error": str(exc)}
                )
        return {
            "autolaunch_por_defecto": AUTOCAD_AUTOLAUNCH_DEFAULT,
            "timeout_espera_s": AUTOCAD_WAIT_TIMEOUT,
            "intervalo_espera_s": AUTOCAD_WAIT_INTERVAL,
            "localserver32": AutoCADConnection._obtener_localserver32() or "",
            "candidatos": candidatos,
            "proceso_acad_detectado": proceso_count > 0,
            "procesos_acad": proceso_count,
        }

    def list_entities(self) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        for ent in self._iter_collection_items(self.model_space):
            entities.append(self._entity_info(ent))
        return entities

    def _entity_info(self, ent: Any) -> dict[str, Any]:
        return {
            "handle": str(getattr(ent, "Handle", "")),
            "tipo": str(getattr(ent, "ObjectName", "")),
            "layer": str(getattr(ent, "Layer", "")),
            "color": int(getattr(ent, "Color", 256)),
        }

    def _get_entity_by_handle(self, handle: str) -> Any:
        for ent in self._iter_collection_items(self.model_space):
            if str(getattr(ent, "Handle", "")).lower() == handle.lower():
                return ent
        return None

    def _get_last_entity(self) -> Any:
        count = int(self.model_space.Count)
        if count == 0:
            raise AutoCADError("No hay entidades en el modelo.")
        return self.model_space.Item(count - 1)

    def delete_entity(self, handle: str) -> dict[str, Any]:
        ent = self._get_entity_by_handle(handle)
        if ent is None:
            raise AutoCADError(f"Entidad con handle '{handle}' no encontrada.")
        ent.Delete()
        return {"ok": True, "handle": handle, "mensaje": "Entidad borrada."}

    def delete_last_entity(self) -> dict[str, Any]:
        try:
            count = int(self.model_space.Count)
            if count == 0:
                return {"ok": False, "error": "No hay entidades para borrar."}
            last_ent = self._get_last_entity()
            handle = str(getattr(last_ent, "Handle", ""))
            last_ent.Delete()
            return {"ok": True, "handle": handle, "mensaje": "Entidad borrada."}
        except AutoCADError:
            raise
        except (COMError, AttributeError, TypeError) as exc:
            raise AutoCADError(f"No se pudo borrar la entidad: {exc}")

    def get_entity_info(self, handle: str) -> dict[str, Any]:
        ent = self._get_entity_by_handle(handle)
        if ent is None:
            raise AutoCADError(f"Entidad con handle '{handle}' no encontrada.")
        info = self._entity_info(ent)
        obj_name = str(getattr(ent, "ObjectName", ""))
        # Para lineas
        if "AcDbLine" in obj_name:
            try:
                info["punto_inicio"] = str(getattr(ent, "StartPoint", ""))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["punto_fin"] = str(getattr(ent, "EndPoint", ""))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["longitud"] = float(getattr(ent, "Length", 0))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["angulo"] = float(getattr(ent, "Angle", 0))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
        # Para polilineas
        if "AcDbPolyline" in obj_name:
            try:
                coords = getattr(ent, "Coordinates", None)
                if coords is not None:
                    pts = []
                    for i in range(0, len(coords), 2):
                        pts.append({"x": float(coords[i]), "y": float(coords[i + 1])})
                    info["coordenadas"] = pts
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["cerrada"] = bool(getattr(ent, "Closed", False))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["area"] = float(getattr(ent, "Area", 0))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["longitud"] = float(getattr(ent, "Length", 0))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
        # Para dimensiones (cotas)
        if "AcDbDimension" in obj_name:
            try:
                info["medicion"] = float(getattr(ent, "Measurement", 0))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["texto_override"] = str(getattr(ent, "TextOverride", ""))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["texto"] = str(getattr(ent, "TextString", ""))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["angulo_rotacion"] = float(getattr(ent, "Rotation", 0))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
        # Para textos
        if "AcDbText" in obj_name or "AcDbMText" in obj_name:
            try:
                info["texto"] = str(getattr(ent, "TextString", ""))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["altura"] = float(getattr(ent, "Height", 0))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
        # Para bloques
        if "AcDbBlockReference" in obj_name:
            try:
                pos = getattr(ent, "InsertionPoint", None)
                if pos is not None:
                    info["insercion"] = {"x": float(pos[0]), "y": float(pos[1])}
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
            try:
                info["nombre_bloque"] = str(getattr(ent, "Name", ""))
            except (AttributeError, TypeError):
                logger.debug("Attribute not available on entity")
        return info

    def get_last_entity_info(self) -> dict[str, Any]:
        ent = self._get_last_entity()
        return self.get_entity_info(str(getattr(ent, "Handle", "")))

    def move_last_entity(self, dx: float, dy: float) -> dict[str, Any]:
        ent = self._get_last_entity()
        try:
            ent.Move(self._point_array(0, 0), self._point_array(dx, dy))
            return {
                "ok": True,
                "handle": str(getattr(ent, "Handle", "")),
                "dx": dx,
                "dy": dy,
            }
        except (COMError, AttributeError, TypeError) as exc:
            raise AutoCADError(f"No se pudo mover la entidad: {exc}")

    def copy_last_entity(self, dx: float, dy: float) -> dict[str, Any]:
        ent = self._get_last_entity()
        try:
            new_ent = ent.Copy()
            try:
                new_ent.Move(self._point_array(0, 0), self._point_array(dx, dy))
            except (AttributeError, TypeError):
                new_ent.Move(self._point_array(0, 0), self._point_array(0, 0))
            return {
                "ok": True,
                "handle_original": str(getattr(ent, "Handle", "")),
                "handle_copia": str(getattr(new_ent, "Handle", "")),
                "dx": dx,
                "dy": dy,
            }
        except (COMError, AttributeError, TypeError) as exc:
            raise AutoCADError(f"No se pudo copiar: {exc}")

    def rotate_last_entity(
        self, angle_deg: float, cx: float = 0, cy: float = 0
    ) -> dict[str, Any]:
        ent = self._get_last_entity()
        try:
            ent.Rotate(self._point_array(cx, cy), math.radians(float(angle_deg)))
            return {
                "ok": True,
                "handle": str(getattr(ent, "Handle", "")),
                "angulo": angle_deg,
            }
        except (COMError, AttributeError, TypeError) as exc:
            raise AutoCADError(f"No se pudo rotar: {exc}")

    def set_last_entity_props(
        self, layer: str | None = None, color: int | None = None
    ) -> dict[str, Any]:
        try:
            last_ent = self._get_last_entity()
            if layer is not None:
                self._safe_set(last_ent, "Layer", layer)
            if color is not None:
                self._safe_set(last_ent, "Color", color)
            return {
                "ok": True,
                "handle": str(getattr(last_ent, "Handle", "")),
                "layer": layer or "",
                "color": color or 256,
            }
        except AutoCADError:
            raise
        except (COMError, AttributeError, TypeError) as exc:
            raise AutoCADError(f"No se pudieron asignar propiedades: {exc}")

    def set_entity_props(
        self, handle: str, layer: str | None = None, color: int | None = None
    ) -> dict[str, Any]:
        ent = self._get_entity_by_handle(handle)
        if ent is None:
            raise AutoCADError(f"Entidad con handle '{handle}' no encontrada.")
        if layer is not None:
            self._safe_set(ent, "Layer", layer)
        if color is not None:
            self._safe_set(ent, "Color", color)
        return {
            "ok": True,
            "handle": handle,
            "layer": layer or "",
            "color": color or 256,
        }

    ENTITY_TYPE_MAP: ClassVar[dict[str, str]] = {
        "linea": "AcDbLine",
        "line": "AcDbLine",
        "circulo": "AcDbCircle",
        "circle": "AcDbCircle",
        "arco": "AcDbArc",
        "arc": "AcDbArc",
        "polilinea": "AcDbPolyline",
        "polyline": "AcDbPolyline",
        "texto": "AcDbText",
        "text": "AcDbText",
        "mtexto": "AcDbMText",
        "mtext": "AcDbMText",
        "cota": "AcDbAlignedDimension",
        "dimension": "AcDbAlignedDimension",
        "dim": "AcDbAlignedDimension",
        "bloque": "AcDbBlockReference",
        "block": "AcDbBlockReference",
        "insert": "AcDbBlockReference",
        "tramas": "AcDbHatch",
        "hatch": "AcDbHatch",
        "spline": "AcDbSpline",
        "elipse": "AcDbEllipse",
        "ellipse": "AcDbEllipse",
        "rayo": "AcDbRay",
        "ray": "AcDbRay",
        "lineaaux": "AcDbXline",
        "xline": "AcDbXline",
    }

    def set_entities_layer_by_type(self, tipo: str, layer: str) -> list[dict[str, Any]]:
        modificados: list[dict[str, Any]] = []
        tipo_lower = tipo.lower().strip()
        target = self.ENTITY_TYPE_MAP.get(tipo_lower, tipo)
        for ent in self._iter_collection_items(self.model_space):
            obj_name = str(getattr(ent, "ObjectName", ""))
            match = target.lower() in obj_name.lower()
            if match:
                self._safe_set(ent, "Layer", layer)
                modificados.append(
                    {
                        "handle": str(getattr(ent, "Handle", "")),
                        "tipo": obj_name,
                        "layer": layer,
                    }
                )
        return modificados

    @staticmethod
    def parse_dimension(texto: str) -> tuple[float, float]:
        clean_text = str(texto).lower().replace("\u00d7", "x")
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*x\s*(\d+(?:[.,]\d+)?)", clean_text)
        if not match:
            raise AutoCADError(
                "No se pudieron leer las dimensiones. Use formato '20 x 20'."
            )
        ancho = float(match.group(1).replace(",", "."))
        largo = float(match.group(2).replace(",", "."))
        if ancho <= 0 or largo <= 0:
            raise AutoCADError("Las dimensiones deben ser mayores que cero.")
        return ancho, largo
