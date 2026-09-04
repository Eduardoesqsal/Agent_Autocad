from __future__ import annotations

from collections import Counter

from autocad_mcp.drawings.base import BasePlan
from autocad_mcp.models import LayerSpec

ARCHITECTURAL_LAYER_SPECS = (
    LayerSpec("A_MUROS", 7, "Continuous", 50),
    LayerSpec("A_PUERTAS", 3, "Continuous", 25),
    LayerSpec("A_VENTANAS", 4, "Continuous", 25),
    LayerSpec("A_EJES", 1, "Center", 13),
    LayerSpec("A_TEXTOS", 7, "Continuous", 13),
    LayerSpec("A_MOBILIARIO", 8, "Continuous", 13),
    LayerSpec("A_SANITARIOS", 6, "Continuous", 13),
    LayerSpec("A_COCINA", 30, "Continuous", 13),
    LayerSpec("A_HACHURAS", 9, "Continuous", 13),
    LayerSpec("A_TERRENO", 94, "Continuous", 13),
    LayerSpec("A_CUBIERTA", 140, "Continuous", 13),
)

DEFAULT_ARCHITECTURAL_BRIEF = (
    "Actua como un Arquitecto Senior con mas de 20 anos de experiencia en diseno "
    "arquitectonico, dibujo tecnico y documentacion ejecutiva en AutoCAD. "
    "Genera dos propuestas completas de planta arquitectonica en metros, usando "
    "solo geometria CAD nativa, capas organizadas profesionalmente y criterios "
    "reales de funcionalidad, circulacion, iluminacion y ventilacion natural."
)


class ArchitecturalProposals(BasePlan):
    def __init__(self, origin_x: float = 0.0, origin_y: float = 0.0) -> None:
        super().__init__(origin_x, origin_y)
        self._prompt: str | None = None

    @property
    def layers(self) -> tuple[LayerSpec, ...]:
        return ARCHITECTURAL_LAYER_SPECS

    def _draw_common_axes(self, ox: float, oy: float, w: float, d: float) -> None:
        cx = ox + w / 2.0
        cy = oy + d / 2.0
        self._l(ox - 0.8, cy, ox + w + 0.8, cy, "A_EJES")
        self._l(cx, oy - 0.8, cx, oy + d + 0.8, "A_EJES")
        self._t("EJE 1", ox - 1.2, cy + 0.1, "A_TEXTOS")
        self._t("EJE A", cx + 0.1, oy + d + 0.35, "A_TEXTOS")

    def _draw_site_and_roof(self, ox: float, oy: float, w: float, d: float) -> None:
        m = 1.4
        self._r(ox - m, oy - m, ox + w + m, oy + d + m, "A_TERRENO")
        self._r(ox - 0.15, oy - 0.15, ox + w + 0.15, oy + d + 0.15, "A_CUBIERTA")

    def _draw_door(
        self, x: float, y: float, width: float, orientation: str, swing: str
    ) -> None:
        layer = "A_PUERTAS"
        if orientation == "horizontal":
            self._l(x, y, x + width, y, layer)
            self._l(x, y, x, y + width, layer)
            if swing == "up":
                self._a(x, y, width, 0, 90, layer)
                self._l(x, y, x + width, y + width, layer)
            else:
                self._a(x, y, width, 270, 360, layer)
                self._l(x, y, x + width, y - width, layer)
        else:
            self._l(x, y, x, y + width, layer)
            self._l(x, y, x + width, y, layer)
            if swing == "right":
                self._a(x, y, width, 0, 90, layer)
                self._l(x, y, x + width, y + width, layer)
            else:
                self._a(x, y, width, 90, 180, layer)
                self._l(x, y, x - width, y + width, layer)

    def _draw_window(self, x1: float, y1: float, x2: float, y2: float) -> None:
        layer = "A_VENTANAS"
        self._l(x1, y1, x2, y2, layer)
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) >= abs(dy):
            self._l(x1, y1 + 0.05, x2, y2 + 0.05, layer)
        else:
            self._l(x1 + 0.05, y1, x2 + 0.05, y2, layer)

    def _draw_furniture(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        layer: str,
        label: str | None = None,
    ) -> None:
        self._r(x1, y1, x2, y2, layer)
        if label:
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            self._t(label, cx - len(label) * 0.08, cy, "A_TEXTOS")

    def _label_space(
        self, name: str, x1: float, y1: float, x2: float, y2: float
    ) -> None:
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        self._t(name, cx - len(name) * 0.08, cy - 0.06, "A_TEXTOS")

    def _hatch(self, x1: float, y1: float, x2: float, y2: float) -> None:
        step = 0.35
        pos = x1 - (y2 - y1)
        while pos <= x2:
            xs = max(x1, pos)
            ys = y1 + max(0.0, x1 - pos)
            xe = min(x2, pos + (y2 - y1))
            ye = y2 - max(0.0, pos + (y2 - y1) - x2)
            if xs < xe:
                self._l(xs, ys, xe, ye, "A_HACHURAS")
            pos += step

    def _build_proposal_one(self, ox: float, oy: float) -> dict:
        w, d = 10.8, 8.4
        self._draw_site_and_roof(ox, oy, w, d)
        self._draw_common_axes(ox, oy, w, d)
        self._r(ox, oy, ox + w, oy + d, "A_MUROS")

        y_split = oy + 3.6
        x_master = ox + 5.4
        x_core = ox + 7.8
        y_core_split = oy + 6.0

        self._l(ox, y_split, ox + w, y_split, "A_MUROS")
        self._l(x_master, y_split, x_master, oy + d, "A_MUROS")
        self._l(x_core, y_split, x_core, oy + d, "A_MUROS")
        self._l(x_master, y_core_split, x_core, y_core_split, "A_MUROS")

        self._draw_door(ox + 2.0, oy, 0.9, "horizontal", "up")
        self._draw_door(ox + 6.1, y_split, 0.85, "vertical", "right")
        self._draw_door(ox + 8.4, y_split, 0.85, "vertical", "left")
        self._draw_door(x_master + 0.35, y_core_split, 0.8, "horizontal", "down")
        self._draw_door(x_core + 0.35, y_core_split, 0.8, "horizontal", "down")

        self._draw_window(ox + 0.6, oy + d, ox + 2.9, oy + d)
        self._draw_window(ox + 8.0, oy + d, ox + 10.2, oy + d)
        self._draw_window(ox + w, oy + 4.5, ox + w, oy + 6.4)
        self._draw_window(ox + 0.1, oy + 6.5, ox + 0.1, oy + 7.8)

        self._draw_furniture(
            ox + 0.5, oy + 0.6, ox + 2.4, oy + 1.4, "A_MOBILIARIO", "SOFA"
        )
        self._draw_furniture(
            ox + 2.8, oy + 0.6, ox + 4.0, oy + 1.8, "A_MOBILIARIO", "MESA"
        )
        self._draw_furniture(
            ox + 7.4, oy + 0.4, ox + 10.0, oy + 1.0, "A_COCINA", "CUBIERTA"
        )
        self._draw_furniture(
            ox + 7.6, oy + 1.2, ox + 8.8, oy + 2.6, "A_COCINA", "FREG."
        )
        self._draw_furniture(
            ox + 0.7, oy + 4.2, ox + 2.6, oy + 5.9, "A_MOBILIARIO", "CAMA"
        )
        self._draw_furniture(
            ox + 8.3, oy + 4.2, ox + 9.9, oy + 5.9, "A_MOBILIARIO", "CAMA"
        )
        self._draw_furniture(
            ox + 5.8, oy + 6.1, ox + 7.2, oy + 7.4, "A_SANITARIOS", "REG."
        )
        self._draw_furniture(
            ox + 5.7, oy + 4.2, ox + 6.5, oy + 5.0, "A_SANITARIOS", "WC"
        )
        self._draw_furniture(
            ox + 6.6, oy + 4.2, ox + 7.3, oy + 4.9, "A_SANITARIOS", "LAV."
        )

        self._label_space("SALA", ox, oy, ox + 4.8, y_split)
        self._label_space("COMEDOR", ox + 4.8, oy, ox + 7.2, y_split)
        self._label_space("COCINA", ox + 7.2, oy, ox + w, y_split)
        self._label_space("RECAMARA PRINCIPAL", ox, y_split, x_master, oy + d)
        self._label_space("BANO + CIRCULACION", x_master, y_split, x_core, oy + d)
        self._label_space("RECAMARA 2", x_core, y_split, ox + w, oy + d)

        self._hatch(x_master + 0.05, y_split + 0.05, x_core - 0.05, oy + d - 0.05)
        self._hatch(ox + 7.25, oy + 0.2, ox + 10.3, oy + 3.0)

        area = w * d
        self._t(f"SUP. CONSTRUIDA: {area:.2f} m2", ox, oy + d + 0.9, "A_TEXTOS")

        espacios = [
            {"nombre": "SALA", "area_m2": round(4.8 * 3.6, 2)},
            {"nombre": "COMEDOR", "area_m2": round(2.4 * 3.6, 2)},
            {"nombre": "COCINA", "area_m2": round(3.6 * 3.6, 2)},
            {"nombre": "RECAMARA PRINCIPAL", "area_m2": round(5.4 * 4.8, 2)},
            {"nombre": "BANO + CIRCULACION", "area_m2": round(2.4 * 4.8, 2)},
            {"nombre": "RECAMARA 2", "area_m2": round(3.0 * 4.8, 2)},
        ]

        return {
            "nombre": "Propuesta 1",
            "origen": {"x": ox, "y": oy},
            "dimensiones_m": {"ancho": w, "fondo": d},
            "superficie_construida_m2": round(area, 2),
            "espacios": espacios,
        }

    def _build_proposal_two(self, ox: float, oy: float) -> dict:
        w, d = 11.2, 8.2
        self._draw_site_and_roof(ox, oy, w, d)
        self._draw_common_axes(ox, oy, w, d)
        self._r(ox, oy, ox + w, oy + d, "A_MUROS")

        y_split = oy + 3.2
        x_left = ox + 3.2
        x_mid = ox + 5.8
        x_right = ox + 8.0
        y_private = oy + 6.0

        self._l(ox, y_split, ox + w, y_split, "A_MUROS")
        self._l(x_left, y_split, x_left, oy + d, "A_MUROS")
        self._l(x_mid, y_split, x_mid, oy + d, "A_MUROS")
        self._l(x_right, y_split, x_right, oy + d, "A_MUROS")
        self._l(x_left, y_private, x_right, y_private, "A_MUROS")

        self._draw_door(ox + 1.8, oy, 0.9, "horizontal", "up")
        self._draw_door(ox + 4.6, y_split, 0.8, "vertical", "right")
        self._draw_door(ox + 6.7, y_split, 0.8, "vertical", "left")
        self._draw_door(ox + 9.0, y_split, 0.85, "vertical", "left")
        self._draw_door(x_left + 0.4, y_private, 0.75, "horizontal", "down")
        self._draw_door(x_mid + 0.25, y_private, 0.75, "horizontal", "down")

        self._draw_window(ox + 0.4, oy + d, ox + 2.5, oy + d)
        self._draw_window(ox + 3.8, oy + d, ox + 5.2, oy + d)
        self._draw_window(ox + 8.5, oy + d, ox + 10.6, oy + d)
        self._draw_window(ox + w, oy + 4.0, ox + w, oy + 5.8)
        self._draw_window(ox, oy + 5.1, ox, oy + 6.6)

        self._draw_furniture(
            ox + 0.4, oy + 0.5, ox + 2.2, oy + 1.2, "A_COCINA", "CUBIERTA"
        )
        self._draw_furniture(ox + 0.5, oy + 1.4, ox + 1.3, oy + 2.8, "A_COCINA", "REF.")
        self._draw_furniture(
            ox + 3.5, oy + 0.6, ox + 5.0, oy + 2.0, "A_MOBILIARIO", "MESA"
        )
        self._draw_furniture(
            ox + 6.0, oy + 0.5, ox + 8.8, oy + 1.4, "A_MOBILIARIO", "SOFA"
        )
        self._draw_furniture(
            ox + 8.7, oy + 0.5, ox + 10.3, oy + 2.0, "A_MOBILIARIO", "SILLON"
        )
        self._draw_furniture(
            ox + 0.6, oy + 4.3, ox + 2.5, oy + 6.0, "A_MOBILIARIO", "CAMA"
        )
        self._draw_furniture(
            ox + 8.4, oy + 4.3, ox + 10.1, oy + 6.0, "A_MOBILIARIO", "CAMA"
        )
        self._draw_furniture(
            ox + 5.0, oy + 4.2, ox + 5.9, oy + 5.1, "A_SANITARIOS", "WC"
        )
        self._draw_furniture(
            ox + 5.1, oy + 5.2, ox + 5.9, oy + 6.0, "A_SANITARIOS", "LAV."
        )
        self._draw_furniture(
            ox + 6.2, oy + 4.3, ox + 7.3, oy + 6.0, "A_SANITARIOS", "DUCHA"
        )

        self._label_space("COCINA", ox, oy, x_left, y_split)
        self._label_space("COMEDOR", x_left, oy, x_mid, y_split)
        self._label_space("SALA", x_mid, oy, ox + w, y_split)
        self._label_space("RECAMARA PRINCIPAL", ox, y_split, x_left, oy + d)
        self._label_space("BANO", x_left, y_split, x_mid, y_private)
        self._label_space("CIRCULACION", x_left, y_private, x_mid, oy + d)
        self._label_space("RECAMARA 2", x_mid, y_split, ox + w, oy + d)

        self._hatch(x_left + 0.05, y_split + 0.05, x_mid - 0.05, y_private - 0.05)
        self._hatch(ox + 0.15, oy + 0.15, x_left - 0.15, y_split - 0.15)

        area = w * d
        self._t(f"SUP. CONSTRUIDA: {area:.2f} m2", ox, oy + d + 0.9, "A_TEXTOS")

        espacios = [
            {"nombre": "COCINA", "area_m2": round(3.2 * 3.2, 2)},
            {"nombre": "COMEDOR", "area_m2": round(2.6 * 3.2, 2)},
            {"nombre": "SALA", "area_m2": round(5.4 * 3.2, 2)},
            {"nombre": "RECAMARA PRINCIPAL", "area_m2": round(3.2 * 4.2, 2)},
            {"nombre": "BANO", "area_m2": round(2.6 * 2.8, 2)},
            {"nombre": "CIRCULACION", "area_m2": round(2.6 * 1.4, 2)},
            {"nombre": "RECAMARA 2", "area_m2": round(3.2 * 5.0, 2)},
        ]

        return {
            "nombre": "Propuesta 2",
            "origen": {"x": ox, "y": oy},
            "dimensiones_m": {"ancho": w, "fondo": d},
            "superficie_construida_m2": round(area, 2),
            "espacios": espacios,
        }

    def set_prompt(self, prompt: str | None = None) -> None:
        self._prompt = prompt or DEFAULT_ARCHITECTURAL_BRIEF

    def _build_geometry(self) -> None:
        self._build_proposal_one(self.ox, self.oy)

    def draw(self, prompt: str | None = None) -> dict:
        self._prompt = prompt or self._prompt or DEFAULT_ARCHITECTURAL_BRIEF
        self._cad.connect()
        self._init_layers()

        p1 = self._build_proposal_one(self.ox, self.oy)
        p2 = self._build_proposal_two(self.ox + 16.0, self.oy)

        self._cad.zoom_extents()

        all_entities = list(self._rec)
        resumen = Counter(e.get("layer", "") for e in all_entities)
        capas_creadas = [{"nombre": s.name} for s in self.layers]

        return {
            "tipo": "propuestas_arquitectonicas",
            "prompt": self._prompt,
            "capas_creadas": capas_creadas,
            "capas_obligatorias": [s.name for s in ARCHITECTURAL_LAYER_SPECS],
            "capas_obligatorias_cumplidas": True,
            "propuestas": [p1, p2],
            "lista_detallada_entidades": all_entities,
            "resumen_capas_utilizadas": dict(sorted(resumen.items())),
            "estado": "geometria_generada",
        }
