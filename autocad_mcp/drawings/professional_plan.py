from __future__ import annotations

from typing import Any

from autocad_mcp.drawings.base import BasePlan
from autocad_mcp.models import LayerSpec


class ProfessionalPlan(BasePlan):
    @property
    def layers(self) -> tuple[LayerSpec, ...]:
        return (
            LayerSpec("A-WALL", 7, "Continuous", 50),
            LayerSpec("A-WALL-HATCH", 9, "Continuous", 13),
            LayerSpec("A-DOOR", 3, "Continuous", 25),
            LayerSpec("A-DOOR-SWING", 3, "Continuous", 13),
            LayerSpec("A-WINDOW", 4, "Continuous", 25),
            LayerSpec("A-WINDOW-GLAZ", 4, "Continuous", 13),
            LayerSpec("A-FLOR", 6, "Continuous", 13),
            LayerSpec("A-FURN", 8, "Continuous", 13),
            LayerSpec("A-KITC", 30, "Continuous", 13),
            LayerSpec("A-SANI", 6, "Continuous", 13),
            LayerSpec("A-DIM", 2, "Continuous", 13),
            LayerSpec("A-ANNO-TEXT", 7, "Continuous", 13),
            LayerSpec("A-ANNO-REDL", 1, "Continuous", 13),
            LayerSpec("A-EJE", 1, "Center2", 13),
            LayerSpec("A-EJE-TEXT", 1, "Continuous", 13),
            LayerSpec("A-SECCION", 6, "Continuous", 35),
            LayerSpec("A-NORTE", 3, "Continuous", 25),
            LayerSpec("A-TERRACE", 140, "Continuous", 13),
            LayerSpec("A-AREA", 7, "Continuous", 13),
            LayerSpec("A-ESCALA", 7, "Continuous", 13),
        )

    def _bed(self, x: float, y: float, w: float, h: float) -> None:
        self._r(x, y, x + w, y + h, "A-FURN")
        self._r(x + 0.08, y + h * 0.55, x + w * 0.42, y + h * 0.88, "A-FURN")
        self._r(x + w * 0.58, y + h * 0.55, x + w * 0.92, y + h * 0.88, "A-FURN")
        self._r(x + 0.05, y + 0.05, x + w * 0.38, y + h * 0.42, "A-FURN")

    def _toilet(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.50, y + 0.30, "A-SANI")
        self._c(x + 0.25, y + 0.50, 0.22, "A-SANI")

    def _lavabo(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.50, y + 0.35, "A-SANI")
        self._c(x + 0.25, y + 0.17, 0.10, "A-SANI")

    def _shower(self, x: float, y: float, w: float) -> None:
        self._r(x, y, x + w, y + w, "A-SANI")
        self._c(x + w / 2, y + w / 2, w * 0.20, "A-SANI")

    def _stove(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.55, "A-KITC")
        for dx, dy in [(0.15, 0.15), (0.15, 0.40), (0.45, 0.15), (0.45, 0.40)]:
            self._c(x + dx, y + dy, 0.05, "A-KITC")

    def _fridge(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.60, "A-KITC")
        self._l(x + 0.08, y + 0.30, x + 0.52, y + 0.30, "A-KITC")

    def _sink(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.70, y + 0.45, "A-KITC")
        self._c(x + 0.17, y + 0.22, 0.09, "A-KITC")
        self._c(x + 0.53, y + 0.22, 0.09, "A-KITC")

    def _sofa(self, x: float, y: float, w: float, h: float) -> None:
        self._r(x, y, x + w, y + h, "A-FURN")
        self._r(x + 0.08, y + 0.10, x + w - 0.08, y + h * 0.80, "A-FURN")
        self._c(x + w / 4, y + h / 2, h * 0.12, "A-FURN")
        self._c(x + w * 3 / 4, y + h / 2, h * 0.12, "A-FURN")

    def _table(self, x: float, y: float, w: float, h: float) -> None:
        self._r(x, y, x + w, y + h, "A-FURN")
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
            self._c(x + w / 2 + ox, y + h / 2 + oy, 0.12, "A-FURN")

    def _washer(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.60, "A-KITC")
        self._c(x + 0.30, y + 0.30, 0.12, "A-KITC")
        self._r(x + 0.05, y + 0.50, x + 0.25, y + 0.55, "A-KITC")
        self._r(x + 0.35, y + 0.50, x + 0.55, y + 0.55, "A-KITC")

    def _dryer(self, x: float, y: float) -> None:
        self._r(x, y, x + 0.60, y + 0.60, "A-KITC")
        self._c(x + 0.30, y + 0.30, 0.14, "A-KITC")

    def _build_geometry(self) -> None:
        ox, oy = self.ox, self.oy
        W, D = 12.0, 13.0
        wall_y = oy + 6.0

        self._wall_rect(ox, oy, ox + W, oy + D, "A-WALL", "A-WALL-HATCH")

        self._r(ox, oy + D, ox + 3.0, oy + D + 2.0, "A-TERRACE")
        self._hatch_rect(
            ox + 0.05, oy + D + 0.05, ox + 2.95, oy + D + 1.95, "A-TERRACE"
        )

        self._wall_line(ox, wall_y, ox + W, wall_y, 0.15, "A-WALL", "A-WALL-HATCH")
        self._wall_line(
            ox + 3.0, wall_y, ox + 3.0, oy + D, 0.15, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(ox + 6.0, oy, ox + 6.0, wall_y, 0.15, "A-WALL", "A-WALL-HATCH")
        self._wall_line(
            ox + 3.0, oy + 1.8, ox + 6.0, oy + 1.8, 0.10, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(ox + 8.5, oy, ox + 8.5, wall_y, 0.15, "A-WALL", "A-WALL-HATCH")
        self._wall_line(
            ox + 6.0, oy + 3.0, ox + 8.5, oy + 3.0, 0.10, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(
            ox + 8.5, oy, ox + 8.5, oy + 3.0, 0.15, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(
            ox + 8.5, wall_y, ox + 12.0, wall_y, 0.15, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(
            ox + 10.0, wall_y, ox + 10.0, oy + D, 0.15, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(ox, wall_y, ox, oy + D, 0.25, "A-WALL", "A-WALL-HATCH")
        self._wall_line(
            ox + 3.0, oy + 9.5, ox + 3.0, oy + D, 0.15, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(
            ox, oy + 9.5, ox + 3.0, oy + 9.5, 0.15, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(
            ox + 1.5, oy + 9.5, ox + 1.5, oy + D, 0.10, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(
            ox + 10.0, oy + 8.5, ox + 12.0, oy + 8.5, 0.15, "A-WALL", "A-WALL-HATCH"
        )
        self._wall_line(
            ox + 3.0, oy + 6.0, ox + 3.0, oy + 13.0, 0.15, "A-WALL", "A-WALL-HATCH"
        )

        doors = [
            (1.5, oy + D, 0.90, "h", "up"),
            (3.0, 7.5, 0.85, "v", "r"),
            (4.5, wall_y, 0.80, "h", "d"),
            (6.0, 4.0, 0.85, "v", "l"),
            (6.7, oy, 0.80, "h", "up"),
            (0.8, wall_y, 0.85, "h", "d"),
            (0.8, 9.5, 0.75, "h", "d"),
            (1.8, 9.5, 0.70, "h", "d"),
            (3.0, 8.5, 0.80, "v", "r"),
            (8.0, 6.0, 0.80, "h", "d"),
            (7.0, 3.0, 0.70, "h", "d"),
            (8.5, 1.5, 0.75, "v", "l"),
            (10.0, 9.5, 0.80, "v", "l"),
            (8.5, 4.5, 0.70, "v", "l"),
        ]
        for dx, dy, w, o, s in doors:
            self._door(ox + dx, oy + dy, w, o, s, "A-DOOR", "A-DOOR-SWING")

        windows = [
            (0.5, oy + D, 2.5, oy + D),
            (3.5, oy + D, 5.5, oy + D),
            (8.5, oy + D, 10.5, oy + D),
            (ox, 10.5, ox, 12.5),
            (ox + W, 0.5, ox + W, 2.5),
            (ox + W, 7.0, ox + W, 9.0),
            (10.5, 6.0, 10.5, 8.0),
            (3.5, 6.0, 5.5, 6.0),
        ]
        for x1, y1, x2, y2 in windows:
            self._win(ox + x1, oy + y1, ox + x2, oy + y2, "A-WINDOW", "A-WINDOW-GLAZ")

        self._sofa(ox + 0.3, oy + 7.0, 1.8, 0.70)
        self._sofa(ox + 0.3, oy + 9.0, 1.2, 0.70)
        self._table(ox + 1.5, oy + 7.8, 0.80, 0.80)
        self._c(ox + 2.5, oy + 8.5, 0.15, "A-FURN")
        self._c(ox + 2.5, oy + 7.3, 0.15, "A-FURN")
        self._table(ox + 3.5, oy + 3.5, 1.20, 0.80)

        self._r(ox + 6.5, oy + 0.3, ox + 11.5, oy + 1.0, "A-KITC")
        self._stove(ox + 7.0, oy + 0.35)
        self._fridge(ox + 10.0, oy + 0.35)
        self._sink(ox + 8.0, oy + 0.35)
        self._r(ox + 7.5, oy + 1.8, ox + 10.0, oy + 2.6, "A-KITC")
        self._c(ox + 8.75, oy + 2.2, 0.15, "A-KITC")
        self._c(ox + 8.0, oy + 2.2, 0.10, "A-KITC")
        self._c(ox + 9.5, oy + 2.2, 0.10, "A-KITC")

        self._toilet(ox + 6.2, oy + 3.2)
        self._lavabo(ox + 6.8, oy + 3.2)
        self._shower(ox + 7.5, oy + 3.2, 0.90)
        self._washer(ox + 8.7, oy + 0.2)
        self._dryer(ox + 9.5, oy + 0.2)

        self._bed(ox + 1.0, oy + 6.8, 1.60, 2.00)
        self._r(ox + 2.8, oy + 6.8, ox + 3.2, oy + 7.2, "A-FURN")
        self._r(ox + 2.8, oy + 7.6, ox + 3.2, oy + 8.0, "A-FURN")
        self._r(ox + 0.3, oy + 6.5, ox + 0.7, oy + 8.5, "A-FURN")

        self._toilet(ox + 0.2, oy + 10.0)
        self._lavabo(ox + 1.8, oy + 9.8)
        self._shower(ox + 0.2, oy + 11.0, 1.00)
        self._r(ox + 1.5, oy + 11.0, ox + 2.8, oy + 12.0, "A-SANI")
        self._r(ox + 0.8, oy + 10.0, ox + 1.3, oy + 11.0, "A-FURN")
        self._r(ox + 0.8, oy + 11.5, ox + 1.3, oy + 12.5, "A-FURN")

        self._bed(ox + 3.3, oy + 6.5, 1.40, 1.80)
        self._r(ox + 4.9, oy + 6.5, ox + 5.2, oy + 6.9, "A-FURN")
        self._r(ox + 3.3, oy + 8.5, ox + 3.8, oy + 9.5, "A-FURN")

        self._bed(ox + 8.3, oy + 7.0, 1.40, 1.80)
        self._r(ox + 9.9, oy + 7.0, ox + 10.2, oy + 7.4, "A-FURN")
        self._r(ox + 8.3, oy + 9.0, ox + 8.8, oy + 10.0, "A-FURN")

        self._r(ox + 3.3, oy, ox + 4.5, oy + 0.5, "A-FLOR")
        self._r(ox + 4.8, oy, ox + 5.5, oy + 0.5, "A-FLOR")

        for eje_x in [oy + D / 2, wall_y]:
            self._l(ox - 0.5, eje_x, ox + W + 0.5, eje_x, "A-EJE")
        for eje_y in [ox + W / 2, ox + 3.0, ox + 6.0, ox + 10.0]:
            self._l(eje_y, oy - 0.5, eje_y, oy + D + 0.5, "A-EJE")

        self._t("EJE 1", ox - 0.8, oy + D / 2 - 0.06, "A-EJE-TEXT", 0.10)
        self._t("EJE 2", ox - 0.8, wall_y - 0.06, "A-EJE-TEXT", 0.10)
        for i, x in enumerate([W / 2, 3.0, 6.0, 10.0]):
            self._t(
                f"EJE {chr(65 + i)}", ox + x - 0.3, oy + D + 0.4, "A-EJE-TEXT", 0.10
            )

        self._dim_h(ox, oy - 0.5, W, "A-DIM")
        self._dim_v(ox - 0.5, oy, D, "A-DIM")

        self._l(ox - 0.3, oy + D + 0.3, ox - 0.3, oy + 7.0, "A-SECCION")
        self._l(ox - 0.3, oy + 7.0, ox + 0.3, oy + 6.4, "A-SECCION")
        self._l(ox - 0.3, oy + 7.0, ox - 0.9, oy + 6.4, "A-SECCION")
        self._t("CORTE A", ox - 0.8, oy + D + 0.5, "A-SECCION", 0.08)

        labels = [
            ("SALA", 0, 6.0, 3.0, 13.0),
            ("FOYER", 3.0, 0, 6.0, 1.8),
            ("COMEDOR", 3.0, 1.8, 6.0, 6.0),
            ("COCINA", 6.0, 0, 12.0, 6.0),
            ("BANO 2", 6.0, 3.0, 8.5, 6.0),
            ("LAVANDERIA", 8.5, 0, 12.0, 3.0),
            ("HALL", 3.0, 6.0, 6.0, 13.0),
            ("RECAMARA\nPRINCIPAL", 0, 6.0, 3.0, 9.5),
            ("BANO\nPRINCIPAL", 0, 9.5, 1.5, 13.0),
            ("W.I.C.", 1.5, 9.5, 3.0, 13.0),
            ("RECAMARA 2", 6.0, 6.0, 10.0, 13.0),
            ("RECAMARA 3", 10.0, 6.0, 12.0, 13.0),
            ("TERRAZA", 0, 13.0, 3.0, 15.0),
        ]
        for name, x1, y1, x2, y2 in labels:
            cx, cy = self._cad._text_center(ox + x1, oy + y1, ox + x2, oy + y2)
            self._t(
                name,
                cx - len(name.split(chr(10))[0]) * 0.055,
                cy - 0.06,
                "A-ANNO-TEXT",
                0.15,
            )

        tx, ty = ox + W + 1.5, oy + D - 1.5
        areas = [
            ("SALA", 3.0 * 7.0),
            ("FOYER", 3.0 * 1.8),
            ("COMEDOR", 3.0 * 4.2),
            ("COCINA", 6.0 * 6.0),
            ("BANO 2", 2.5 * 3.0),
            ("LAVANDERIA", 3.5 * 3.0),
            ("HALL", 3.0 * 7.0),
            ("RECAMARA PRINCIPAL", 3.0 * 3.5),
            ("BANO PRINCIPAL", 1.5 * 3.5),
            ("W.I.C.", 1.5 * 3.5),
            ("RECAMARA 2", 4.0 * 7.0),
            ("RECAMARA 3", 2.0 * 7.0),
            ("TERRAZA", 3.0 * 2.0),
        ]
        total = sum(a for _, a in areas)
        n = len(areas)
        w_tab, h_tab = 9.0, n * 0.45 + 0.6
        self._r(tx, ty - h_tab, tx + w_tab, ty, "A-AREA")
        self._r(tx + 0.1, ty - 0.2, tx + w_tab - 0.1, ty - 0.55, "A-AREA")
        self._t("CUADRO DE AREAS", tx + 2.5, ty - 0.45, "A-AREA", 0.18)
        self._l(tx, ty - 0.6, tx + w_tab, ty - 0.6, "A-AREA")
        for i, (nom, sup) in enumerate(areas):
            yy = ty - 0.75 - i * 0.45
            self._l(tx, yy, tx + w_tab, yy, "A-AREA")
            self._l(tx + 6.5, yy, tx + 6.5, yy + 0.45, "A-AREA")
            self._t(nom, tx + 0.3, yy + 0.08, "A-AREA", 0.06)
            self._t(f"{sup:.2f} m2", tx + 6.8, yy + 0.08, "A-AREA", 0.06)
        yy_tot = ty - 0.75 - n * 0.45
        self._l(tx, yy_tot, tx + w_tab, yy_tot, "A-AREA")
        self._t("TOTAL:", tx + 0.3, yy_tot - 0.35, "A-AREA", 0.08)
        self._t(f"{total:.2f} m2", tx + 6.8, yy_tot - 0.35, "A-AREA", 0.08)

        self._arrow_north(ox + W + 4.5, oy + 4.5, "A-NORTE", "A-NORTE")

        sx, sy = ox + W + 2.0, oy + 2.5
        segs, seg_w = 4, 2.0
        for i in range(segs):
            xs = sx + i * seg_w
            self._r(xs, sy, xs + seg_w, sy + 0.4, "A-ESCALA" if i % 2 == 0 else "A-DIM")
        self._t("0", sx - 0.2, sy - 0.3, "A-ESCALA", 0.06)
        self._t("4m", sx + segs * seg_w - 0.1, sy - 0.3, "A-ESCALA", 0.06)
        self._t("ESCALA GRAFICA 1:50", sx + 0.5, sy + 0.6, "A-ESCALA", 0.08)

        self._t(
            "PLANTA ARQUITECTONICA", ox + W / 2 - 2.0, oy - 1.8, "A-ANNO-TEXT", 0.20
        )
        self._t(
            f"PROYECTO: CASA HABITACION  |  SUPERFICIE: {total:.2f} m2  |  ESC: 1:50",
            ox + W / 2 - 3.5,
            oy - 2.2,
            "A-ANNO-TEXT",
            0.08,
        )
        self._t(
            "FECHA: JUNIO 2026  |  ARQ. MCP AUTOMATION",
            ox + W / 2 - 2.5,
            oy - 2.5,
            "A-ANNO-TEXT",
            0.06,
        )

    def draw(self) -> dict[str, Any]:
        result = super().draw()
        areas = [
            ("SALA", 21.0),
            ("FOYER", 5.4),
            ("COMEDOR", 12.6),
            ("COCINA", 36.0),
            ("BANO 2", 7.5),
            ("LAVANDERIA", 10.5),
            ("HALL", 21.0),
            ("RECAMARA PRINCIPAL", 10.5),
            ("BANO PRINCIPAL", 5.25),
            ("W.I.C.", 5.25),
            ("RECAMARA 2", 28.0),
            ("RECAMARA 3", 14.0),
            ("TERRAZA", 6.0),
        ]
        total = sum(a for _, a in areas)
        result.update(
            {
                "tipo": "planta_arquitectonica_profesional",
                "dimensiones": {"ancho": 12.0, "fondo": 13.0},
                "superficie_total_m2": round(total, 2),
                "capas": [s.name for s in self.layers],
                "espacios": [n for n, _ in areas],
            }
        )
        return result
