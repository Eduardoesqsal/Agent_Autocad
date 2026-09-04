from __future__ import annotations

import math
from typing import Any


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x2 - x1, y2 - y1)


def midpoint(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def angle(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def cross_product_sign(
    x1: float, y1: float, x2: float, y2: float, x3: float, y3: float
) -> float:
    return (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)


def perpendicular_offset(
    x1: float, y1: float, x2: float, y2: float, distancia: float, outward: bool = True
) -> tuple[float, float]:
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return 0.0, 0.0
    if outward:
        return -dy / length * distancia, dx / length * distancia
    else:
        return dy / length * distancia, -dx / length * distancia


def get_polyline_vertices(entity: Any) -> list[tuple[float, float]]:
    coords = list(entity.Coordinates)
    vertices: list[tuple[float, float]] = []
    for i in range(0, len(coords), 2):
        vertices.append((float(coords[i]), float(coords[i + 1])))
    closed = bool(getattr(entity, "Closed", False))
    if closed and len(vertices) > 2:
        vertices.append(vertices[0])
    return vertices


def polygon_area(vertices: list[tuple[float, float]]) -> float:
    area = 0.0
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def find_last_closed_polyline(conn: Any) -> Any | None:
    from autocad_mcp.core.autocad import AutoCADConnection

    for ent in reversed(AutoCADConnection._iter_collection_items(conn.model_space)):
        tipo = str(getattr(ent, "ObjectName", ""))
        if "AcDbPolyline" in tipo:
            closed = bool(getattr(ent, "Closed", False))
            if closed:
                return ent
    return None
