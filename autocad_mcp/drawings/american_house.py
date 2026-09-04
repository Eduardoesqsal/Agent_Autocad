from __future__ import annotations

from typing import Any

from autocad_mcp.drawings.base import BasePlan
from autocad_mcp.models import LayerSpec


class AmericanHousePlan(BasePlan):
    @property
    def layers(self) -> tuple[LayerSpec, ...]:
        return (
            LayerSpec("A-MUROS", 7, "Continuous", 50),
            LayerSpec("A-MUROS-HATCH", 9, "Continuous", 13),
            LayerSpec("A-PUERTAS", 3, "Continuous", 25),
            LayerSpec("A-VENTANAS", 4, "Continuous", 25),
            LayerSpec("A-EJES", 1, "Center", 13),
            LayerSpec("A-COTAS", 2, "Continuous", 13),
            LayerSpec("A-TEXTOS", 7, "Continuous", 13),
            LayerSpec("A-MOBILIARIO", 8, "Continuous", 13),
            LayerSpec("A-COCINA", 30, "Continuous", 13),
            LayerSpec("A-SANITARIOS", 6, "Continuous", 13),
            LayerSpec("A-GARAJE", 3, "Continuous", 25),
            LayerSpec("A-PORCHE", 140, "Continuous", 25),
            LayerSpec("A-PAVIMENTO", 253, "Continuous", 13),
            LayerSpec("A-JARDIN", 3, "Continuous", 13),
            LayerSpec("A-AGUA", 5, "Continuous", 13),
            LayerSpec("A-LIMITE", 94, "Continuous", 13),
            LayerSpec("A-ESCALA", 7, "Continuous", 13),
        )

    def _bed(self, x: float, y: float, w: float, h: float) -> None:
        self._r(x, y, x + w, y + h, "A-MOBILIARIO")
        self._r(x + 0.08, y + h * 0.55, x + w * 0.42, y + h * 0.88, "A-MOBILIARIO")
        self._r(x + w * 0.58, y + h * 0.55, x + w * 0.92, y + h * 0.88, "A-MOBILIARIO")
        self._r(x + 0.05, y + 0.05, x + w * 0.38, y + h * 0.42, "A-MOBILIARIO")

    def _toilet(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.50, y + 0.30, "A-SANITARIOS")
        self._c(x + 0.25, y + 0.50, 0.22, "A-SANITARIOS")

    def _lavabo(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.50, y + 0.35, "A-SANITARIOS")
        self._c(x + 0.25, y + 0.17, 0.10, "A-SANITARIOS")

    def _shower(self, x: float, y: float, w: float) -> None:
        self._r(x, y, x + w, y + w, "A-SANITARIOS")
        self._c(x + w / 2, y + w / 2, w * 0.20, "A-SANITARIOS")

    def _stove(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.55, "A-COCINA")
        for dx, dy in [(0.15, 0.15), (0.15, 0.40), (0.45, 0.15), (0.45, 0.40)]:
            self._c(x + dx, y + dy, 0.05, "A-COCINA")

    def _fridge(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.60, "A-COCINA")
        self._l(x + 0.08, y + 0.30, x + 0.52, y + 0.30, "A-COCINA")

    def _sink(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.70, y + 0.45, "A-COCINA")
        self._c(x + 0.17, y + 0.22, 0.09, "A-COCINA")
        self._c(x + 0.53, y + 0.22, 0.09, "A-COCINA")

    def _sofa(self, x: float, y: float, w: float, h: float) -> None:
        self._r(x, y, x + w, y + h, "A-MOBILIARIO")
        self._r(x + 0.08, y + 0.10, x + w - 0.08, y + h * 0.80, "A-MOBILIARIO")
        self._c(x + w / 4, y + h / 2, h * 0.12, "A-MOBILIARIO")
        self._c(x + w * 3 / 4, y + h / 2, h * 0.12, "A-MOBILIARIO")

    def _table(self, x: float, y: float, w: float, h: float) -> None:
        self._r(x, y, x + w, y + h, "A-MOBILIARIO")
        for ox, oy in [
            (-0.25, 0),
            (w + 0.25, 0),
            (0, -0.25),
            (0, h + 0.25),
            (-0.25, -0.25),
            (-0.25, h + 0.25),
            (w + 0.25, -0.25),
            (w + 0.25, h + 0.25),
        ]:
            self._c(x + w / 2 + ox, y + h / 2 + oy, 0.12, "A-MOBILIARIO")

    def _washer(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.60, "A-COCINA")
        self._c(x + 0.30, y + 0.30, 0.12, "A-COCINA")
        self._r(x + 0.05, y + 0.50, x + 0.25, y + 0.55, "A-COCINA")
        self._r(x + 0.35, y + 0.50, x + 0.55, y + 0.55, "A-COCINA")

    def _dryer(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.60, "A-COCINA")
        self._c(x + 0.30, y + 0.30, 0.14, "A-COCINA")

    def _mesa_noche(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.50, y + 0.50, "A-MOBILIARIO")
        self._c(x + 0.25, y + 0.25, 0.08, "A-MOBILIARIO")

    def _closet(self, x: float, y: float, w: float, h: float) -> None:
        self._r(x, y, x + w, y + h, "A-MOBILIARIO")
        self._l(x + 0.10, y, x + 0.10, y + h, "A-MOBILIARIO")
        self._l(x + w - 0.10, y, x + w - 0.10, y + h, "A-MOBILIARIO")

    def _build_geometry(self) -> None:
        ox, oy = self.ox, self.oy
        W, D = 10.0, 20.0

        self._wall_line(ox, oy, ox + W, oy, 0.25, "A-MUROS", "A-MUROS-HATCH")
        self._wall_line(ox + W, oy, ox + W, oy + D, 0.25, "A-MUROS", "A-MUROS-HATCH")
        self._wall_line(ox + W, oy + D, ox, oy + D, 0.25, "A-MUROS", "A-MUROS-HATCH")
        self._wall_line(ox, oy + D, ox, oy, 0.25, "A-MUROS", "A-MUROS-HATCH")

        self._wall_line(
            ox, oy + 5.0, ox + W, oy + 5.0, 0.15, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox, oy + 10.0, ox + W, oy + 10.0, 0.15, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox + 5.0, oy, ox + 5.0, oy + 5.0, 0.15, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox + 5.0, oy + 5.0, ox + 5.0, oy + 10.0, 0.15, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox + 3.5, oy + 10.0, ox + 3.5, oy + D, 0.15, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox + 6.5, oy + 10.0, ox + 6.5, oy + D, 0.15, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox + 5.0, oy + 14.0, ox + 6.5, oy + 14.0, 0.10, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox + 3.5, oy + 15.0, ox + 6.5, oy + 15.0, 0.10, "A-MUROS", "A-MUROS-HATCH"
        )
        self._wall_line(
            ox + 5.0, oy + 10.0, ox + 5.0, oy + 14.0, 0.10, "A-MUROS", "A-MUROS-HATCH"
        )

        self._door(ox + 2.0, oy + 5.0, 0.80, "h", "up", "A-PUERTAS", "A-PUERTAS")
        self._door(ox + 3.5, oy + 10.0, 0.80, "h", "up", "A-PUERTAS", "A-PUERTAS")
        self._door(ox + 6.5, oy + 10.0, 0.80, "h", "up", "A-PUERTAS", "A-PUERTAS")
        self._door(ox + 5.0, oy + 3.0, 0.70, "v", "r", "A-PUERTAS", "A-PUERTAS")
        self._door(ox + 5.0, oy + 7.0, 0.70, "v", "l", "A-PUERTAS", "A-PUERTAS")
        self._door(ox + 5.0, oy + 12.0, 0.70, "v", "l", "A-PUERTAS", "A-PUERTAS")
        self._door(ox + 2.0, oy + 15.0, 0.70, "h", "d", "A-PUERTAS", "A-PUERTAS")

        self._win(ox + 1.5, oy + D, ox + 4.5, oy + D, "A-VENTANAS", "A-VENTANAS")
        self._win(ox + 7.0, oy + D, ox + 9.5, oy + D, "A-VENTANAS", "A-VENTANAS")
        self._win(ox, oy + 2.0, ox, oy + 4.0, "A-VENTANAS", "A-VENTANAS")
        self._win(ox + W, oy + 7.0, ox + W, oy + 9.0, "A-VENTANAS", "A-VENTANAS")
        self._win(ox + 1.5, oy + 5.0, ox + 3.5, oy + 5.0, "A-VENTANAS", "A-VENTANAS")
        self._win(ox + 0.5, oy + 12.0, ox + 2.5, oy + 12.0, "A-VENTANAS", "A-VENTANAS")
        self._win(ox + 7.5, oy + 14.0, ox + 9.5, oy + 14.0, "A-VENTANAS", "A-VENTANAS")

        self._sofa(ox + 0.5, oy + 0.5, 2.0, 0.80)
        self._sofa(ox + 0.5, oy + 2.0, 1.2, 0.70)
        self._table(ox + 1.5, oy + 1.3, 0.70, 0.70)
        self._c(ox + 3.0, oy + 0.8, 0.15, "A-MOBILIARIO")
        self._c(ox + 3.0, oy + 2.0, 0.15, "A-MOBILIARIO")
        self._r(ox + 3.5, oy + 0.3, ox + 4.5, oy + 0.7, "A-MOBILIARIO")

        self._r(ox + 6.0, oy + 0.3, ox + 9.5, oy + 1.0, "A-COCINA")
        self._stove(ox + 6.5, oy + 0.35)
        self._fridge(ox + 8.5, oy + 0.35)
        self._sink(ox + 7.2, oy + 0.35)
        self._r(ox + 6.0, oy + 2.0, ox + 8.5, oy + 2.8, "A-COCINA")
        self._c(ox + 6.5, oy + 2.4, 0.12, "A-COCINA")
        self._c(ox + 7.5, oy + 2.4, 0.12, "A-COCINA")
        self._c(ox + 8.0, oy + 2.4, 0.12, "A-COCINA")

        self._table(ox + 1.5, oy + 6.0, 1.50, 0.90)
        self._r(ox + 3.5, oy + 5.5, ox + 4.5, oy + 6.0, "A-MOBILIARIO")
        self._r(ox + 3.5, oy + 6.5, ox + 4.5, oy + 7.0, "A-MOBILIARIO")

        self._toilet(ox + 6.0, oy + 5.5)
        self._lavabo(ox + 7.0, oy + 5.5)
        self._shower(ox + 8.0, oy + 5.5, 1.0)
        self._r(ox + 6.0, oy + 7.5, ox + 8.0, oy + 8.0, "A-SANITARIOS")

        self._washer(ox + 6.0, oy + 8.5)
        self._dryer(ox + 7.0, oy + 8.5)
        self._r(ox + 8.5, oy + 8.5, ox + 9.5, oy + 9.5, "A-COCINA")

        self._bed(ox + 0.8, oy + 11.0, 1.60, 2.00)
        self._mesa_noche(ox + 0.3, oy + 11.5)
        self._mesa_noche(ox + 2.3, oy + 11.5)
        self._closet(ox + 0.5, oy + 10.5, 0.40, 0.60)
        self._r(ox + 1.5, oy + 13.5, ox + 2.5, oy + 14.0, "A-MOBILIARIO")

        self._toilet(ox + 0.3, oy + 15.5)
        self._lavabo(ox + 1.5, oy + 15.5)
        self._shower(ox + 0.3, oy + 17.0, 1.2)
        self._r(ox + 2.0, oy + 17.0, ox + 3.0, oy + 18.5, "A-SANITARIOS")

        self._bed(ox + 7.0, oy + 11.0, 1.40, 1.90)
        self._mesa_noche(ox + 6.8, oy + 11.8)
        self._mesa_noche(ox + 8.8, oy + 11.8)
        self._closet(ox + 7.0, oy + 10.5, 0.80, 0.50)

        self._bed(ox + 4.0, oy + 11.5, 1.60, 2.00)
        self._mesa_noche(ox + 3.8, oy + 12.0)
        self._closet(ox + 4.5, oy + 10.5, 0.60, 0.50)

        self._toilet(ox + 4.0, oy + 15.5)
        self._lavabo(ox + 5.0, oy + 15.5)
        self._shower(ox + 4.0, oy + 17.0, 1.0)
        self._r(ox + 5.5, oy + 17.0, ox + 6.0, oy + 18.0, "A-SANITARIOS")

        self._r(ox + 7.0, oy + 15.5, ox + 9.5, oy + 19.5, "A-GARAJE")
        self._r(ox + 7.3, oy + 16.0, ox + 8.0, oy + 17.0, "A-GARAJE")
        self._r(ox + 8.5, oy + 16.0, ox + 9.2, oy + 17.0, "A-GARAJE")
        self._l(ox + 7.3, oy + 18.0, ox + 9.2, oy + 18.0, "A-GARAJE")
        self._l(ox + 7.3, oy + 18.0, ox + 7.3, oy + 19.5, "A-GARAJE")
        self._l(ox + 9.2, oy + 18.0, ox + 9.2, oy + 19.5, "A-GARAJE")

        self._r(ox + 0.5, oy + D - 1.0, ox + 4.0, oy + D + 1.5, "A-PORCHE")
        self._l(ox + 0.5, oy + D - 1.0, ox + 0.5, oy + D + 1.5, "A-PORCHE")
        self._l(ox + 4.0, oy + D - 1.0, ox + 4.0, oy + D + 1.5, "A-PORCHE")
        self._l(ox + 0.5, oy + D + 1.5, ox + 4.0, oy + D + 1.5, "A-PORCHE")
        self._c(ox + 1.2, oy + D + 0.5, 0.15, "A-PORCHE")
        self._c(ox + 2.8, oy + D + 0.5, 0.15, "A-PORCHE")

        self._c(ox + 7.0, oy + 7.0, 0.40, "A-JARDIN")
        self._c(ox + 8.5, oy + 7.0, 0.30, "A-JARDIN")
        self._c(ox + 7.5, oy + 6.5, 0.25, "A-JARDIN")

        self._r(ox + 6.0, oy + 1.0, ox + 9.0, oy + 3.5, "A-AGUA")
        self._t("ALBERCA", ox + 7.0, oy + 2.0, "A-AGUA", 0.25)

        self._l(ox - 0.5, oy + D / 2, ox + W + 0.5, oy + D / 2, "A-EJES")
        self._l(ox + W / 2, oy - 0.5, ox + W / 2, oy + D + 0.5, "A-EJES")
        self._l(ox - 0.5, oy + 5.0, ox + W + 0.5, oy + 5.0, "A-EJES")
        self._l(ox + 5.0, oy - 0.5, ox + 5.0, oy + D + 0.5, "A-EJES")

        self._dim_h(ox, oy - 0.5, W, "A-COTAS")
        self._dim_v(ox - 0.5, oy, D, "A-COTAS")

        labels = [
            ("SALA\nRECIBIDOR", ox, oy, ox + 5.0, oy + 5.0),
            ("COCINA", ox + 5.0, oy, ox + W, oy + 5.0),
            ("COMEDOR", ox, oy + 5.0, ox + 5.0, oy + 10.0),
            ("BANO 1", ox + 5.0, oy + 5.0, ox + W, oy + 10.0),
            ("RECAMARA 1", ox, oy + 10.0, ox + 3.5, oy + 15.0),
            ("RECAMARA 2", ox + 6.5, oy + 10.0, ox + W, oy + 15.0),
            ("RECAMARA 3", ox + 3.5, oy + 10.0, ox + 6.5, oy + 15.0),
            ("BANO\nPRIVADO", ox, oy + 15.0, ox + 3.5, oy + D),
            ("BANO\nCOMPARTIDO", ox + 3.5, oy + 15.0, ox + 6.5, oy + D),
            ("GARAJE", ox + 6.5, oy + 15.0, ox + W, oy + D),
        ]
        for name, x1, y1, x2, y2 in labels:
            cx, cy = self._cad._text_center(x1, y1, x2, y2)
            self._t(name, cx - 0.5, cy - 0.10, "A-TEXTOS", 0.20)

        self._t("CUADRO DE AREAS", ox + W + 2.0, oy + D - 2.5, "A-TEXTOS", 0.3)
        yt = oy + D - 3.0
        espacios = [
            ("SALA", 3.5 * 4.0),
            ("COMEDOR", 3.5 * 5.0),
            ("COCINA", 6.0 * 5.0),
            ("RECAMARA PRINCIPAL", 3.5 * 2.5),
            ("BANO PRINCIPAL", 3.5 * 2.5),
            ("RECAMARA 2", 3.5 * 2.5),
            ("BANO", 2.0 * 2.5),
            ("PASILLO", 1.5 * 2.5),
            ("LAVANDERIA", 2.5 * 2.0),
            ("GARAJE", 6.0 * 4.0),
            ("PORCHE", 5.5 * 2.5),
            ("FOYER", 3.5 * 1.5),
        ]
        self._r(
            ox + W + 1.5, yt - len(espacios) * 0.4, ox + W + 7.0, yt + 0.4, "A-TEXTOS"
        )
        for i, (nom, sup) in enumerate(espacios):
            yy = yt - i * 0.4
            self._l(ox + W + 1.5, yy, ox + W + 7.0, yy, "A-TEXTOS")
            self._t(nom, ox + W + 1.7, yy - 0.28, "A-TEXTOS", 0.18)
            self._t(f"{sup:.1f} m2", ox + W + 5.0, yy - 0.28, "A-TEXTOS", 0.18)
        total_area = sum(s for _, s in espacios)
        self._t(
            f"TOTAL: {total_area:.1f} m2",
            ox + W + 1.7,
            yt - len(espacios) * 0.4 - 0.35,
            "A-TEXTOS",
            0.22,
        )
        self._t(
            "SUP. TERRENO: 200 m2",
            ox + W + 1.7,
            yt - len(espacios) * 0.4 - 0.7,
            "A-TEXTOS",
            0.22,
        )

        self._t("ESCALA GRAFICA", ox + 0.5, oy - 3.5, "A-ESCALA", 0.2)
        for i in range(10):
            bx = ox + 0.5 + i * 1.0
            self._r(
                bx,
                oy - 4.2,
                bx + 1.0,
                oy - 3.8,
                "A-ESCALA" if i % 2 == 0 else "A-TEXTOS",
            )
        self._t("0", ox + 0.3, oy - 4.5, "A-ESCALA", 0.15)
        self._t("5m", ox + 5.3, oy - 4.5, "A-ESCALA", 0.15)
        self._t("10m", ox + 10.3, oy - 4.5, "A-ESCALA", 0.15)

        self._arrow_north(ox + W + 3.5, oy + D - 4.5, "A-EJES", "A-EJES")

    def draw(self) -> dict[str, Any]:
        result = super().draw()
        espacios = [
            ("SALA", 3.5 * 4.0),
            ("COMEDOR", 3.5 * 5.0),
            ("COCINA", 6.0 * 5.0),
            ("RECAMARA PRINCIPAL", 3.5 * 2.5),
            ("BANO PRINCIPAL", 3.5 * 2.5),
            ("RECAMARA 2", 3.5 * 2.5),
            ("BANO", 2.0 * 2.5),
            ("PASILLO", 1.5 * 2.5),
            ("LAVANDERIA", 2.5 * 2.0),
            ("GARAJE", 6.0 * 4.0),
            ("PORCHE", 5.5 * 2.5),
            ("FOYER", 3.5 * 1.5),
        ]
        total_area = sum(s for _, s in espacios)
        result.update(
            {
                "dimensiones_m": {"ancho": 10.0, "fondo": 20.0},
                "superficie_construida_m2": round(total_area, 2),
                "superficie_terreno_m2": 200,
                "espacios": [
                    {"nombre": n, "area_m2": round(s, 2)} for n, s in espacios
                ],
                "capas": [s.name for s in self.layers],
            }
        )
        return result
