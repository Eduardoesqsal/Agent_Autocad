from __future__ import annotations

import math
import random

from autocad_mcp.drawings.base import BasePlan
from autocad_mcp.models import LayerSpec

TERRENO = [
    (0.0, 0.0),
    (18.0, 1.0),
    (20.0, 17.0),
    (2.0, 19.0),
    (0.0, 12.0),
    (2.0, 8.0),
    (0.0, 4.0),
]

COLINDA = [
    ("NORTE", "Terreno baldio", 20.0, (0, 19), (18, 18)),
    ("ESTE", "Calle principal", 18.0, (18, 18), (20, 17)),
    ("SURESTE", "Terreno vecino A", 15.0, (20, 17), (18, 1)),
    ("SUR", "Calle secundaria", 18.0, (18, 1), (0, 0)),
    ("OESTE", "Terreno vecino B", 16.0, (0, 0), (0, 12)),
    ("NOROESTE", "Terreno vecino C", 8.0, (0, 12), (2, 8)),
    ("NOROESTE 2", "Terreno vecino D", 5.0, (2, 8), (0, 4)),
]


class TopoPlan(BasePlan):
    @property
    def layers(self) -> tuple[LayerSpec, ...]:
        return (
            LayerSpec("TOPO-POLIGONO", 7, "Continuous", 50),
            LayerSpec("TOPO-VERTICE", 1, "Continuous", 25),
            LayerSpec("TOPO-CURVA-MADRE", 9, "Continuous", 25),
            LayerSpec("TOPO-CURVA-NIVEL", 3, "Continuous", 13),
            LayerSpec("TOPO-PUNTO", 1, "Continuous", 13),
            LayerSpec("TOPO-DRENAJE", 5, "TRAZOS", 13),
            LayerSpec("TOPO-TALUD", 6, "Continuous", 13),
            LayerSpec("TOPO-ACCESO", 4, "Continuous", 25),
            LayerSpec("TOPO-COTA", 2, "Continuous", 13),
            LayerSpec("TOPO-MALLA", 8, "Continuous", 13),
            LayerSpec("TOPO-ETIQUETA", 8, "Continuous", 13),
            LayerSpec("TOPO-COLINDANCIA", 3, "Continuous", 25),
            LayerSpec("TOPO-CUADRO-BORDE", 7, "Continuous", 35),
            LayerSpec("TOPO-CUADRO-LINEA", 253, "Continuous", 13),
            LayerSpec("TOPO-CUADRO-TEXTO", 7, "Continuous", 13),
            LayerSpec("TOPO-ROTULO", 7, "Continuous", 13),
            LayerSpec("TOPO-NORTE", 1, "Continuous", 25),
            LayerSpec("TOPO-SOMBREADO", 9, "Continuous", 13),
            LayerSpec("TOPO-RELLENO", 253, "Continuous", 13),
        )

    @staticmethod
    def _dist(x1: float, y1: float, x2: float, y2: float) -> float:
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _malla(self) -> None:
        for i in range(0, 25, 5):
            self._l(self.ox + i, self.oy, self.ox + i, self.oy + 20, "TOPO-MALLA")
            self._t(str(i), self.ox + i - 0.3, self.oy - 0.8, "TOPO-MALLA")
        for i in range(0, 21, 5):
            self._l(self.ox, self.oy + i, self.ox + 24, self.oy + i, "TOPO-MALLA")
            self._t(str(i), self.ox - 1.0, self.oy + i - 0.2, "TOPO-MALLA")

    def _curvas_nivel(self) -> None:
        curves = [
            (
                [
                    (self.ox + x, self.oy + 2 + 0.5 * math.sin(x * 0.8))
                    for x in [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 20.0]
                ],
                "TOPO-CURVA-MADRE",
                102.5,
            ),
            (
                [
                    (self.ox + x, self.oy + 5 + 0.6 * math.sin(x * 0.6 + 0.5))
                    for x in [0.0, 4.0, 8.0, 12.0, 16.0, 20.0]
                ],
                "TOPO-CURVA-NIVEL",
                105.0,
            ),
            (
                [
                    (self.ox + x, self.oy + 8 + 0.5 * math.sin(x * 0.7 + 1.0))
                    for x in [0.0, 3.5, 7.0, 10.5, 14.0, 17.5, 20.0]
                ],
                "TOPO-CURVA-MADRE",
                107.5,
            ),
            (
                [
                    (self.ox + x, self.oy + 11 + 0.4 * math.sin(x * 0.5 + 1.5))
                    for x in [0.0, 5.0, 10.0, 15.0, 20.0]
                ],
                "TOPO-CURVA-NIVEL",
                110.0,
            ),
            (
                [
                    (self.ox + x, self.oy + 14 + 0.5 * math.sin(x * 0.6 + 2.0))
                    for x in [0.0, 4.0, 8.0, 12.0, 16.0, 20.0]
                ],
                "TOPO-CURVA-MADRE",
                112.5,
            ),
        ]
        for pts, layer, elev in curves:
            for i in range(len(pts) - 1):
                self._l(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], layer)
            mp = pts[len(pts) // 2]
            self._t(f"Curva {elev:.1f}", mp[0] + 0.5, mp[1] + 0.3, "TOPO-CURVA-MADRE")

    def _colindancias(self) -> None:
        for nombre, desc, dist, p1, p2 in COLINDA:
            x1 = self.ox + p1[0]
            y1 = self.oy + p1[1]
            x2 = self.ox + p2[0]
            y2 = self.oy + p2[1]
            self._l(x1, y1, x2, y2, "TOPO-COLINDANCIA")
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            ang = math.degrees(math.atan2(dy, dx))
            perp = 0.25
            nx = -dy / self._dist(x1, y1, x2, y2) * perp
            ny = dx / self._dist(x1, y1, x2, y2) * perp
            self._tr(
                f"{desc} ({dist:.1f}m)", mx + nx, my + ny, ang, "TOPO-COLINDANCIA", 0.12
            )

    def _tabla_construccion(self) -> None:
        tx, ty = self.ox + 26, self.oy + 12
        rows = [("VERTICE", "ESTE (X)", "NORTE (Y)", "DISTANCIA", "RUMBO")]
        n = len(TERRENO)
        for i in range(n):
            x, y = TERRENO[i]
            xn, yn = TERRENO[(i + 1) % n]
            d = self._dist(x, y, xn, yn)
            rows.append((f"V{i+1}", f"{x:.3f}", f"{y:.3f}", f"{d:.3f}", f"N{i*45:d}E"))
        rows.append(("", "", "", "", ""))
        th = 0.35
        tw = 10.0
        for i, r in enumerate(rows):
            yy = ty - i * th
            if i == 0:
                self._r(tx, yy - th, tx + tw, yy, "TOPO-CUADRO-BORDE")
            self._l(tx, yy, tx + tw, yy, "TOPO-CUADRO-LINEA")
            col_w = [2.5, 2.5, 2.5, 2.5, 2.5]
            cx = tx
            for j, val in enumerate(r):
                self._t(val, cx + 0.1, yy - 0.25, "TOPO-CUADRO-TEXTO")
                if j < len(col_w) - 1:
                    self._l(
                        cx + col_w[j], yy - th, cx + col_w[j], yy, "TOPO-CUADRO-LINEA"
                    )
                cx += col_w[j]

    def _datos_generales(self) -> None:
        dx, dy = self.ox + 26, self.oy + 6
        self._r(dx, dy, dx + 12, dy + 5, "TOPO-CUADRO-BORDE")
        datos = [
            ("PROYECTO:", "LEVANTAMIENTO TOPOGRAFICO"),
            ("SOLICITA:", "CLIENTE"),
            ("FECHA:", "JUNIO 2026"),
            ("ESCALA:", "1:100"),
            ("SISTEMA:", "UTM WGS84 ZONA 14"),
        ]
        for i, (k, v) in enumerate(datos):
            yy = dy + 4.4 - i * 0.45
            self._t(k, dx + 0.3, yy - 0.1, "TOPO-CUADRO-TEXTO")
            self._t(v, dx + 3.0, yy - 0.1, "TOPO-CUADRO-TEXTO")
            self._l(dx, yy - 0.4, dx + 12, yy - 0.4, "TOPO-CUADRO-LINEA")

    def _norte(self) -> None:
        nx, ny = self.ox + 28, self.oy + 2.5
        self._l(nx, ny - 0.5, nx, ny + 1.5, "TOPO-NORTE")
        self._l(nx, ny + 1.5, nx - 0.4, ny + 0.7, "TOPO-NORTE")
        self._l(nx, ny + 1.5, nx + 0.4, ny + 0.7, "TOPO-NORTE")
        self._t("N", nx - 0.2, ny + 1.8, "TOPO-NORTE")

    def _drenajes(self) -> None:
        pts_list = [
            [(5, 18), (8, 14), (7, 10), (10, 6)],
            [(12, 17), (14, 12), (13, 8)],
            [(3, 15), (5, 11), (4, 7)],
        ]
        for pts in pts_list:
            pts_f = [(self.ox + p[0], self.oy + p[1]) for p in pts]
            for i in range(len(pts_f) - 1):
                self._l(
                    pts_f[i][0],
                    pts_f[i][1],
                    pts_f[i + 1][0],
                    pts_f[i + 1][1],
                    "TOPO-DRENAJE",
                )
            for xs, ys in pts_f:
                self._t("D", xs - 0.2, ys + 0.2, "TOPO-DRENAJE")

    def _taludes(self) -> None:
        self._l(self.ox + 16, self.oy + 16, self.ox + 18, self.oy + 14, "TOPO-TALUD")
        self._l(self.ox + 17, self.oy + 16, self.ox + 19, self.oy + 14, "TOPO-TALUD")
        self._l(self.ox + 2, self.oy + 2, self.ox + 4, self.oy + 0.5, "TOPO-TALUD")
        self._l(self.ox + 3, self.oy + 2, self.ox + 5, self.oy + 0.5, "TOPO-TALUD")
        for i in range(5):
            self._l(
                self.ox + 16.5 + i * 0.25,
                self.oy + 15.8 - i * 0.15,
                self.ox + 17.5 + i * 0.25,
                self.oy + 14.2 - i * 0.15,
                "TOPO-TALUD",
            )
            self._l(
                self.ox + 2.5 + i * 0.25,
                self.oy + 2 - i * 0.15,
                self.ox + 3.5 + i * 0.25,
                self.oy + 0.5 - i * 0.15,
                "TOPO-TALUD",
            )

    def _puntos_control(self) -> None:
        random.seed(123)
        for _ in range(12):
            px = self.ox + 1.5 + random.uniform(0, 17)
            py = self.oy + 1.5 + random.uniform(0, 18)
            elev = 100.0 + random.uniform(0.5, 5.0)
            self._c(px, py, 0.12, "TOPO-PUNTO")
            self._t(f"E{elev:.2f}", px - 0.6, py + 0.3, "TOPO-PUNTO")

    def _relleno_poligono(self) -> None:
        pts = [(self.ox + x, self.oy + y) for x, y in TERRENO]
        min_x = min(p[0] for p in pts)
        max_x = max(p[0] for p in pts)
        min_y = min(p[1] for p in pts)
        max_y = max(p[1] for p in pts)
        step = 0.35
        pos = min_x - (max_y - min_y)
        while pos <= max_x:
            x_start = max(min_x, pos)
            y_start = min_y + max(0.0, min_x - pos)
            x_end = min(max_x, pos + (max_y - min_y))
            y_end = max_y - max(0.0, pos + (max_y - min_y) - max_x)
            if x_start < x_end:
                self._l(x_start, y_start, x_end, y_end, "TOPO-RELLENO")
            pos += step

    def _distancias_lados(self, pts: list[tuple[float, float]]) -> None:
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            d = math.sqrt(dx * dx + dy * dy)
            ang = math.degrees(math.atan2(dy, dx))
            perp = 0.30
            nx = -dy / d * perp
            ny = dx / d * perp
            self._tr(f"{d:.3f}", mx + nx, my + ny, ang, "TOPO-ETIQUETA", 0.10)

    def _build_geometry(self) -> None:
        ox, oy = self.ox, self.oy

        self._malla()
        self._relleno_poligono()

        pts_terreno = [(ox + x, oy + y) for x, y in TERRENO]
        for i in range(len(pts_terreno)):
            x1, y1 = pts_terreno[i]
            x2, y2 = pts_terreno[(i + 1) % len(pts_terreno)]
            self._l(x1, y1, x2, y2, "TOPO-POLIGONO")
        self._distancias_lados(pts_terreno)

        self._curvas_nivel()
        self._puntos_control()
        self._drenajes()
        self._taludes()
        self._colindancias()

        self._tabla_construccion()
        self._datos_generales()
        self._norte()

        n = len(TERRENO)
        for i in range(n):
            vx, vy = pts_terreno[i]
            self._c(vx, vy, 0.15, "TOPO-VERTICE")
            self._t(f"V{i+1}", vx + 0.3, vy + 0.2, "TOPO-VERTICE")

        self._t("PLANO TOPOGRAFICO PLANIMETRICO", ox + 22, oy + 12.5, "TOPO-ROTULO")

    def draw(self) -> dict:
        result = super().draw()
        n = len(TERRENO)
        area2 = sum(
            TERRENO[i][0] * TERRENO[(i + 1) % n][1]
            - TERRENO[(i + 1) % n][0] * TERRENO[i][1]
            for i in range(n)
        )
        area = abs(area2) / 2.0
        perim = sum(
            self._dist(
                TERRENO[i][0],
                TERRENO[i][1],
                TERRENO[(i + 1) % n][0],
                TERRENO[(i + 1) % n][1],
            )
            for i in range(n)
        )
        result.update(
            {
                "tipo": "plano_topografico_planimetrico",
                "terreno": {
                    "vertices": n,
                    "superficie_m2": round(area, 3),
                    "perimetro_m": round(perim, 3),
                },
                "colindancias": COLINDA,
                "capas": [s.name for s in self.layers],
            }
        )
        return result
