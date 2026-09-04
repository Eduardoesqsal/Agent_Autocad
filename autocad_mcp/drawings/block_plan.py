from __future__ import annotations

import logging
from typing import Any

from autocad_mcp.drawings.base import BasePlan
from autocad_mcp.models import LayerSpec

logger = logging.getLogger(__name__)


class BlockPlan(BasePlan):
    def __init__(
        self, origin_x: float = 0.0, origin_y: float = 0.0, limpiar: bool = False
    ) -> None:
        super().__init__(origin_x, origin_y)
        self._limpiar = limpiar

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

    def _blk(
        self,
        nombre: str,
        x: float,
        y: float,
        layer: str,
        escala: float = 1.0,
        rot: float = 0.0,
    ) -> None:
        self._rec.append(self._cad.insert_block(nombre, x, y, escala, rot, layer))

    def _build_geometry(self) -> None:
        if self._limpiar:
            try:
                for i in range(int(self._cad.model_space.Count) - 1, -1, -1):
                    try:
                        self._cad.model_space.Item(i).Delete()
                    except (AttributeError, TypeError):
                        logger.debug("Could not delete entity")
            except (AttributeError, TypeError):
                logger.debug("Could not delete entity")

        ox, oy = self.ox, self.oy
        W, D = 12.0, 13.0
        wall_y = oy + 6.0

        self._wall_rect(ox, oy, ox + W, oy + D, "A-WALL", "A-WALL-HATCH")
        self._r(ox, oy + D, ox + 3.0, oy + D + 2.0, "A-TERRACE")
        self._hatch_rect(
            ox + 0.05, oy + D + 0.05, ox + 2.95, oy + D + 1.95, "A-TERRACE"
        )

        walls = [
            (ox, wall_y, ox + W, wall_y, 0.15),
            (ox + 3.0, wall_y, ox + 3.0, oy + D, 0.15),
            (ox + 6.0, oy, ox + 6.0, wall_y, 0.15),
            (ox + 3.0, oy + 1.8, ox + 6.0, oy + 1.8, 0.10),
            (ox + 8.5, oy, ox + 8.5, wall_y, 0.15),
            (ox + 6.0, oy + 3.0, ox + 8.5, oy + 3.0, 0.10),
            (ox + 8.5, oy, ox + 8.5, oy + 3.0, 0.15),
            (ox + 8.5, wall_y, ox + 12.0, wall_y, 0.15),
            (ox + 10.0, wall_y, ox + 10.0, oy + D, 0.15),
            (ox, wall_y, ox, oy + D, 0.25),
            (ox + 3.0, oy + 9.5, ox + 3.0, oy + D, 0.15),
            (ox, oy + 9.5, ox + 3.0, oy + 9.5, 0.15),
            (ox + 1.5, oy + 9.5, ox + 1.5, oy + D, 0.10),
            (ox + 10.0, oy + 8.5, ox + 12.0, oy + 8.5, 0.15),
            (ox + 3.0, oy + 6.0, ox + 3.0, oy + 13.0, 0.15),
        ]
        for x1, y1, x2, y2, t in walls:
            self._wall_line(x1, y1, x2, y2, t, "A-WALL", "A-WALL-HATCH")

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

        blocks = [
            ("SILLA 1 B. DINAMICO", 0.5, 7.5, "A-FURN", 0.8, 0),
            ("SILLA 1 B. DINAMICO", 0.5, 8.5, "A-FURN", 0.8, 0),
            ("SILLA 1 B. DINAMICO", 0.5, 9.5, "A-FURN", 0.8, 0),
            ("BUTACA", 2.0, 7.5, "A-FURN", 0.8, 180),
            ("BUTACA", 2.0, 8.5, "A-FURN", 0.8, 180),
            ("MESA 4", 1.3, 8.0, "A-FURN", 0.8, 0),
            ("MUEBLE DE TV DINAMICO", 2.5, 9.0, "A-FURN", 0.8, 90),
            ("DECORACION", 2.5, 7.0, "A-FURN", 0.8, 0),
            ("DECORACION", 0.3, 11.0, "A-FURN", 0.8, 0),
            ("MESA 6", 4.5, 3.8, "A-FURN", 0.8, 0),
            ("SILLA 1 B. DINAMICO", 4.5, 3.0, "A-FURN", 0.6, 0),
            ("SILLA 1 B. DINAMICO", 4.5, 4.6, "A-FURN", 0.6, 180),
            ("SILLA 1 B. DINAMICO", 3.8, 3.8, "A-FURN", 0.6, 90),
            ("SILLA 1 B. DINAMICO", 5.2, 3.8, "A-FURN", 0.6, 270),
            ("COCINA 4 HORNILLAS", 7.0, 0.4, "A-KITC", 0.8, 0),
            ("REFRIGERADOR B. DINAMICO", 10.5, 0.5, "A-KITC", 0.6, 0),
            ("LAVAPLATOS DINAMICO MDP", 8.5, 0.4, "A-KITC", 0.7, 0),
            ("CAMPANA EXTRACTORA", 7.0, 1.2, "A-KITC", 0.6, 0),
            ("CAMPANA EXTRACTORA", 8.5, 1.2, "A-KITC", 0.6, 0),
            ("CAMPANA EXTRACTORA", 10.5, 1.2, "A-KITC", 0.6, 0),
            ("GRIFO 1", 8.5, 0.7, "A-KITC", 0.5, 0),
            ("GRIFO 1", 10.5, 0.7, "A-KITC", 0.5, 0),
            ("SILLA 1 B. DINAMICO", 8.0, 1.5, "A-KITC", 0.5, 0),
            ("SILLA 1 B. DINAMICO", 8.8, 1.5, "A-KITC", 0.5, 0),
            ("INODORO PLANTA", 6.4, 3.4, "A-SANI", 0.7, 0),
            ("LAVAMANOS B. DINAMICO", 7.0, 3.4, "A-SANI", 0.6, 0),
            ("REGADERA B. DINAMICO", 7.6, 3.5, "A-SANI", 0.6, 0),
            ("LAVADORA B. DINAMICO", 9.0, 0.5, "A-KITC", 0.6, 0),
            ("LAVADORA T2 DINAMICO", 9.8, 0.5, "A-KITC", 0.6, 0),
            ("SUMIDERO", 11.0, 0.5, "A-KITC", 0.6, 0),
        ]
        for nombre, dx, dy, layer, esc, rot in blocks:
            self._blk(nombre, ox + dx, oy + dy, layer, esc, rot)

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
        for i in range(4):
            xs = sx + i * 2.0
            self._r(xs, sy, xs + 2.0, sy + 0.4, "A-ESCALA" if i % 2 == 0 else "A-DIM")
        self._t("0", sx - 0.2, sy - 0.3, "A-ESCALA", 0.06)
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
            "FECHA: JUNIO 2026  |  ARQ. MCP AUTOMATION (BLOQUES DINAMICOS)",
            ox + W / 2 - 3.0,
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
                "tipo": "planta_arquitectonica_con_bloques",
                "dimensiones": {"ancho": 12.0, "fondo": 13.0},
                "superficie_total_m2": round(total, 2),
                "capas": [s.name for s in self.layers],
                "espacios": [n for n, _ in areas],
            }
        )
        return result
