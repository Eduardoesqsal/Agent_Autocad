from __future__ import annotations

import math
from typing import Any

from autocad_mcp.config import DEFAULT_LAYERS
from autocad_mcp.core.autocad import AutoCADConnection
from autocad_mcp.core.geometry import (
    distance,
    find_last_closed_polyline,
    get_polyline_vertices,
    polygon_area,
)


class ConstructionTableService:
    def __init__(self, conn: AutoCADConnection) -> None:
        self._conn = conn

    def create_construction_table(
        self,
        colindantes: list[str] | None = None,
        altura_texto: float = 0.6,
        escala_header: float = 1.0,
        escala_area: float = 1.0,
    ) -> dict[str, Any]:
        vertices = self._last_closed_polyline_vertices()
        origin_x, origin_y = self._table_origin(vertices)
        detalles = self._build_table(
            vertices,
            origin_x,
            origin_y,
            colindantes,
            altura_texto,
            escala_header,
            escala_area,
        )
        self._conn.zoom_extents()
        return {
            "ok": True,
            "mensaje": f"Cuadro de construccion generado con {len(vertices)} vertices.",
            "detalles": detalles,
        }

    def create_curve_table(self) -> dict[str, Any]:
        vertices = self._last_closed_polyline_vertices()
        origin_x, origin_y = self._table_origin(vertices)
        detalles = self._build_table(vertices, origin_x, origin_y)
        self._conn.zoom_extents()
        return {
            "ok": True,
            "mensaje": f"Cuadro de curvas generado con {len(vertices)} vertices.",
            "detalles": detalles,
        }

    def create_utm_grid(
        self, espaciado: float, tamanio_cruz: float | None = None
    ) -> dict[str, Any]:
        vertices = self._last_closed_polyline_vertices()
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        spacing = float(espaciado)
        half = (
            max(1.0, spacing * 0.1)
            if tamanio_cruz is None
            else float(tamanio_cruz) / 2.0
        )
        text_height = max(0.3, min(1.0, spacing * 0.05))

        gx_min = math.floor(min_x / spacing) * spacing - spacing
        gx_max = math.ceil(max_x / spacing) * spacing + spacing
        gy_min = math.floor(min_y / spacing) * spacing - spacing
        gy_max = math.ceil(max_y / spacing) * spacing + spacing

        layer = "RETICULA"
        self._conn.ensure_layer(layer, color=DEFAULT_LAYERS[layer])

        total = 0
        x = gx_min
        while x <= gx_max:
            y = gy_min
            while y <= gy_max:
                self._conn.add_line(x - half, y, x + half, y, layer=layer)
                self._conn.add_line(x, y - half, x, y + half, layer=layer)
                total += 1
                y += spacing
            x += spacing

        x = gx_min
        while x <= gx_max:
            self._conn.add_text(
                f"{x:.3f}",
                x,
                gy_min - spacing * 0.5,
                text_height,
                layer=layer,
                rotacion=90,
            )
            x += spacing

        y = gy_min
        while y <= gy_max:
            self._conn.add_text(
                f"{y:.3f}",
                gx_min - spacing * 0.5,
                y - spacing * 0.02,
                text_height,
                layer=layer,
            )
            y += spacing

        self._conn.zoom_extents()
        return {
            "ok": True,
            "mensaje": f"Reticula UTM cada {spacing}m con {total} cruces.",
        }

    def _last_closed_polyline_vertices(self) -> list[tuple[float, float]]:
        poly = find_last_closed_polyline(self._conn)
        if poly is None:
            from autocad_mcp.core.autocad import AutoCADError

            raise AutoCADError("No se encontro ningun poligono cerrado en el dibujo.")
        return get_polyline_vertices(poly)

    @staticmethod
    def _table_origin(vertices: list[tuple[float, float]]) -> tuple[float, float]:
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        min_x, max_x = min(xs), max(xs)
        max_y = max(ys)
        return max_x + (max_x - min_x) * 0.15 + 15, max_y + 10

    def _build_table(
        self,
        vertices: list[tuple[float, float]],
        origin_x: float,
        origin_y: float,
        colindantes: list[str] | None = None,
        altura_texto: float = 0.6,
        escala_header: float = 1.0,
        escala_area: float = 1.0,
    ) -> list[dict[str, Any]]:
        rows = len(vertices)
        has_col = isinstance(colindantes, list) and len(colindantes) >= rows
        h = altura_texto

        dists = [
            distance(*vertices[i], *vertices[(i + 1) % rows]) for i in range(rows)
        ]
        labels = [f"P{i + 1}" for i in range(rows)]
        x_strs = [f"{vx:.3f}" for vx, _ in vertices]
        y_strs = [f"{vy:.3f}" for _, vy in vertices]
        d_strs = [f"{d:.3f}" for d in dists]
        c_strs: list[str] = colindantes if has_col and colindantes is not None else []
        area_val = polygon_area(vertices)
        perim_val = sum(dists)

        headers = ["VERTICE", "X", "Y", "DISTANCIA"]
        if has_col:
            headers.append("COLINDANTE")

        char_w = 1.0 * h
        padding = 0.8 * h
        col_data = [
            [headers[0], *labels],
            [headers[1], *x_strs],
            [headers[2], *y_strs],
            [headers[3], *d_strs],
        ]
        if has_col:
            col_data.append([headers[4], *c_strs])

        col_w = [max(len(s) for s in col) * char_w + 2 * padding for col in col_data]
        row_h = 3.0 * h
        header_h = 3.5 * h
        extra_h = 3.5 * h
        table_layer = "CUADRO_DATOS"
        self._conn.ensure_layer(table_layer, color=DEFAULT_LAYERS[table_layer])

        col_x: list[float] = []
        current_x = origin_x
        for width in col_w:
            col_x.append(current_x)
            current_x += width

        total_w = sum(col_w)
        total_h = header_h + rows * row_h + extra_h
        sep_y = origin_y - header_h - rows * row_h

        def add_line(x1: float, y1: float, x2: float, y2: float) -> None:
            self._conn.add_line(x1, y1, x2, y2, layer=table_layer)

        def add_text(txt: str, x: float, y: float, escala: float = 1.0) -> None:
            self._conn.add_text(txt, x, y, h * escala, layer=table_layer)

        add_line(origin_x, origin_y, origin_x + total_w, origin_y)
        add_line(origin_x, origin_y, origin_x, origin_y - total_h)
        add_line(origin_x + total_w, origin_y, origin_x + total_w, origin_y - total_h)
        add_line(origin_x, origin_y - total_h, origin_x + total_w, origin_y - total_h)
        add_line(origin_x, origin_y - header_h, origin_x + total_w, origin_y - header_h)

        for col_start in col_x[1:]:
            add_line(col_start, origin_y, col_start, sep_y)

        for i, header in enumerate(headers):
            text_x = col_x[i] + col_w[i] / 2 - len(header) * char_w / 2
            text_y = origin_y - header_h / 2 - h * 0.4
            add_text(header, text_x, text_y, escala_header)

        for i in range(rows):
            row_y = origin_y - header_h - i * row_h
            y_pos = row_y - row_h * 0.65
            add_text(labels[i], col_x[0] + padding, y_pos)
            add_text(x_strs[i], col_x[1] + padding, y_pos)
            add_text(y_strs[i], col_x[2] + padding, y_pos)
            add_text(d_strs[i], col_x[3] + padding, y_pos)
            if has_col and i < len(c_strs):
                add_text(c_strs[i], col_x[4] + padding, y_pos)

        add_line(origin_x, sep_y, origin_x + total_w, sep_y)
        area_text = f"AREA: {area_val:.3f} m2"
        perim_text = f"PERIMETRO: {perim_val:.3f} m"
        add_text(area_text, origin_x + padding, sep_y - extra_h * 0.65, escala_area)
        perim_x = origin_x + len(area_text) * char_w + 2.0 * h
        add_text(perim_text, perim_x, sep_y - extra_h * 0.65, escala_area)

        return [
            {
                "tipo": "Tabla",
                "filas": rows,
                "origen_x": origin_x,
                "origen_y": origin_y,
                "area": round(area_val, 3),
                "perimetro": round(perim_val, 3),
            }
        ]

