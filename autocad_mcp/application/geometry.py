from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from autocad_mcp.core.autocad import AutoCADConnection
from autocad_mcp.models import Point2D


class GeometryService:
    def __init__(self, conn: AutoCADConnection) -> None:
        self._conn = conn

    @staticmethod
    def to_points(
        puntos: Iterable[dict[str, Any] | tuple[float, float]],
    ) -> list[Point2D]:
        normalizados: list[Point2D] = []
        for punto in puntos:
            if isinstance(punto, dict):
                normalizados.append(Point2D(float(punto["x"]), float(punto["y"])))
            else:
                x, y = punto
                normalizados.append(Point2D(float(x), float(y)))
        return normalizados

    def create_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        layer: str | None = None,
        color: int | None = None,
    ) -> dict[str, Any]:
        result = self._conn.add_line(x1, y1, x2, y2, layer=layer)
        self._apply_optional_props(layer, color)
        return result

    def create_circle(
        self,
        x: float,
        y: float,
        radio: float,
        *,
        layer: str | None = None,
        color: int | None = None,
    ) -> dict[str, Any]:
        result = self._conn.add_circle(x, y, radio, layer=layer)
        self._apply_optional_props(layer, color)
        return result

    def create_polyline(
        self,
        puntos: list[Any],
        *,
        cerrar: bool = False,
        layer: str | None = None,
        color: int | None = None,
    ) -> dict[str, Any]:
        result = self._conn.add_polyline(
            self.to_points(puntos), cerrar=cerrar, layer=layer
        )
        self._apply_optional_props(layer, color)
        return result

    def create_polygon(
        self, puntos: list[Any], *, layer: str | None = None, color: int | None = None
    ) -> dict[str, Any]:
        return self.create_polyline(puntos, cerrar=True, layer=layer, color=color)

    def insert_text(
        self,
        texto: str,
        x: float,
        y: float,
        altura: float,
        *,
        rotacion: float = 0.0,
    ) -> dict[str, Any]:
        return self._conn.add_text(texto, x, y, altura, rotacion=rotacion)

    def _apply_optional_props(self, layer: str | None, color: int | None) -> None:
        if color is not None:
            self._conn.set_last_entity_props(color=color)
        elif layer:
            self._conn.set_last_entity_props(layer=layer, color=256)
