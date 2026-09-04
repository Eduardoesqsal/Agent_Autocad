from __future__ import annotations

import math
from typing import Any

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError
from autocad_mcp.core.geometry import (
    distance,
    get_polyline_vertices,
    polygon_area,
    find_last_closed_polyline,
)


def _build_table(
    conn: AutoCADConnection,
    vertices: list[tuple[float, float]],
    origin_x: float,
    origin_y: float,
    colindantes: list[str] | None = None,
    altura_texto: float = 0.6,
    escala_header: float = 1.0,
    escala_area: float = 1.0,
) -> list[dict]:
    rows = len(vertices)
    has_col = isinstance(colindantes, list) and len(colindantes) >= rows
    h = altura_texto

    dists: list[float] = []
    for i in range(rows):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % rows]
        dists.append(distance(x1, y1, x2, y2))
    labels = [f"P{i+1}" for i in range(rows)]
    x_strs = [f"{vx:.3f}" for vx, vy in vertices]
    y_strs = [f"{vy:.3f}" for vx, vy in vertices]
    d_strs = [f"{d:.3f}" for d in dists]
    c_strs: list[str] = colindantes if has_col and colindantes is not None else []
    area_val = polygon_area(vertices)
    perim_val = sum(dists)

    headers = ["VERTICE", "X", "Y", "DISTANCIA"]
    if has_col:
        headers.append("COLINDANTE")

    cw = 1.0 * h
    pad_i = 0.8 * h

    col_data_strs = [
        [headers[0]] + labels,
        [headers[1]] + x_strs,
        [headers[2]] + y_strs,
        [headers[3]] + d_strs,
    ]
    if has_col:
        col_data_strs.append([headers[4]] + c_strs)

    col_w = [max(len(s) for s in col) * cw + 2 * pad_i for col in col_data_strs]

    row_h = 3.0 * h
    header_h = 3.5 * h
    extra_h = 3.5 * h
    start_x = origin_x
    start_y = origin_y
    table_layer = "CUADRO_DATOS"
    conn.ensure_layer(table_layer, color=2)

    col_x: list[float] = []
    cx = start_x
    for w in col_w:
        col_x.append(cx)
        cx += w

    total_w = sum(col_w)
    total_h = header_h + rows * row_h + extra_h

    def add_line(x1, y1, x2, y2):
        conn.add_line(x1, y1, x2, y2, layer=table_layer)

    def add_text(txt, x, y, escala=1.0):
        conn.add_text(txt, x, y, h * escala, layer=table_layer)

    # border
    add_line(start_x, start_y, start_x + total_w, start_y)
    add_line(start_x, start_y, start_x, start_y - total_h)
    add_line(start_x + total_w, start_y, start_x + total_w, start_y - total_h)
    add_line(start_x, start_y - total_h, start_x + total_w, start_y - total_h)

    # header separator
    add_line(start_x, start_y - header_h, start_x + total_w, start_y - header_h)

    # vertical separators (only through data rows, not area/perimeter row)
    sep_y = start_y - header_h - rows * row_h
    for cx_item in col_x[1:]:
        add_line(cx_item, start_y, cx_item, sep_y)

    # header text (centered in column)
    for i, hdr in enumerate(headers):
        cx_h = col_x[i] + col_w[i] / 2
        cy_h = start_y - header_h / 2
        add_text(hdr, cx_h - len(hdr) * cw / 2, cy_h - h * 0.4, escala_header)

    # data rows
    for i, (vx, vy) in enumerate(vertices):
        row_y = start_y - header_h - i * row_h
        y_pos = row_y - row_h * 0.65
        add_text(labels[i], col_x[0] + pad_i, y_pos)
        add_text(x_strs[i], col_x[1] + pad_i, y_pos)
        add_text(y_strs[i], col_x[2] + pad_i, y_pos)
        add_text(d_strs[i], col_x[3] + pad_i, y_pos)
        if has_col and i < len(c_strs):
            add_text(c_strs[i], col_x[4] + pad_i, y_pos)

    # area and perimeter row (free text, no column divisions)
    add_line(start_x, sep_y, start_x + total_w, sep_y)
    area_text = f"AREA: {area_val:.3f} m2"
    perim_text = f"PERIMETRO: {perim_val:.3f} m"
    gap = 2.0 * h
    add_text(area_text, start_x + pad_i, sep_y - extra_h * 0.65, escala_area)
    perim_x = start_x + len(area_text) * cw + gap
    add_text(perim_text, perim_x, sep_y - extra_h * 0.65, escala_area)

    return [
        {
            "tipo": "Tabla",
            "filas": rows,
            "origen_x": start_x,
            "origen_y": start_y,
            "area": round(area_val, 3),
            "perimetro": round(perim_val, 3),
        },
    ]


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="cuadro_construccion")
    def tool_cuadro_construccion(
        colindantes: list[str] | None = None,
        altura_texto: float = 0.6,
        escala_header: float = 1.0,
        escala_area: float = 1.0,
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()

            poly = find_last_closed_polyline(conn)
            if poly is None:
                return {
                    "ok": False,
                    "error": "No se encontro ningun poligono cerrado en el dibujo.",
                }

            vertices = get_polyline_vertices(poly)

            # compute bounding box
            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            table_origin_x = max_x + (max_x - min_x) * 0.15 + 15
            table_origin_y = max_y + 10

            result = _build_table(
                conn,
                vertices,
                table_origin_x,
                table_origin_y,
                colindantes,
                altura_texto,
                escala_header,
                escala_area,
            )

            conn.zoom_extents()
            return {
                "ok": True,
                "mensaje": f"Cuadro de construccion generado con {len(vertices)} vertices.",
                "detalles": result,
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="cuadro_curvas")
    def tool_cuadro_curvas() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()

            poly = find_last_closed_polyline(conn)
            if poly is None:
                return {
                    "ok": False,
                    "error": "No se encontro ningun poligono cerrado en el dibujo.",
                }

            vertices = get_polyline_vertices(poly)

            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            table_origin_x = max_x + (max_x - min_x) * 0.15 + 15
            table_origin_y = max_y + 10

            result = _build_table(conn, vertices, table_origin_x, table_origin_y)

            conn.zoom_extents()
            return {
                "ok": True,
                "mensaje": f"Cuadro de curvas generado con {len(vertices)} vertices.",
                "detalles": result,
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="reticula_utm")
    def tool_reticula_utm(espaciado: float, tamanio_cruz: float | None = None) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()

            poly = find_last_closed_polyline(conn)
            if poly is None:
                return {
                    "ok": False,
                    "error": "No se encontro ningun poligono cerrado en el dibujo.",
                }

            vertices = get_polyline_vertices(poly)
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

            gx_min = math.floor(min_x / spacing) * spacing - spacing
            gx_max = math.ceil(max_x / spacing) * spacing + spacing
            gy_min = math.floor(min_y / spacing) * spacing - spacing
            gy_max = math.ceil(max_y / spacing) * spacing + spacing

            layer = "RETICULA"
            conn.ensure_layer(layer, color=8)

            total = 0
            x = gx_min
            while x <= gx_max:
                y = gy_min
                while y <= gy_max:
                    conn.add_line(x - half, y, x + half, y, layer=layer)
                    conn.add_line(x, y - half, x, y + half, layer=layer)
                    total += 1
                    y += spacing
                x += spacing

            x = gx_min
            while x <= gx_max:
                conn.add_text(
                    f"{x:.3f}",
                    x,
                    gy_min - spacing * 0.5,
                    spacing * 0.05,
                    layer=layer,
                    rotacion=90,
                )
                x += spacing
            y = gy_min
            while y <= gy_max:
                conn.add_text(
                    f"{y:.3f}",
                    gx_min - spacing * 0.5,
                    y - spacing * 0.02,
                    spacing * 0.05,
                    layer=layer,
                )
                y += spacing

            conn.zoom_extents()
            return {
                "ok": True,
                "mensaje": f"Retícula UTM cada {spacing}m con {total} cruces.",
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
