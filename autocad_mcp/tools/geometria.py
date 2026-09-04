from __future__ import annotations

from typing import Iterable

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError
from autocad_mcp.models import Point2D


def _to_points(puntos: Iterable[dict | tuple]) -> list[Point2D]:
    normalizados: list[Point2D] = []
    for punto in puntos:
        if isinstance(punto, dict):
            normalizados.append(Point2D(float(punto["x"]), float(punto["y"])))
        else:
            x, y = punto
            normalizados.append(Point2D(float(x), float(y)))
    return normalizados


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="crear_linea")
    def tool_crear_linea(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        capa: str | None = None,
        color: int | None = None,
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            result = conn.add_line(x1, y1, x2, y2, layer=capa)
            if color is not None:
                conn.set_last_entity_props(color=color)
            elif capa:
                conn.set_last_entity_props(layer=capa, color=256)
            return {"ok": True, "data": result}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="crear_circulo")
    def tool_crear_circulo(
        x: float,
        y: float,
        radio: float,
        capa: str | None = None,
        color: int | None = None,
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            result = conn.add_circle(x, y, radio, layer=capa)
            if color is not None:
                conn.set_last_entity_props(color=color)
            elif capa:
                conn.set_last_entity_props(layer=capa, color=256)
            return {"ok": True, "data": result}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="crear_polilinea")
    def tool_crear_polilinea(
        puntos: list,
        cerrar: bool = False,
        capa: str | None = None,
        color: int | None = None,
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            result = conn.add_polyline(_to_points(puntos), cerrar=cerrar, layer=capa)
            if color is not None:
                conn.set_last_entity_props(color=color)
            elif capa:
                conn.set_last_entity_props(layer=capa, color=256)
            return {"ok": True, "data": result}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="crear_poligono")
    def tool_crear_poligono(
        puntos: list, capa: str = "", color: int | None = None
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            capa_val = capa if capa else None
            result = conn.add_polyline(_to_points(puntos), cerrar=True, layer=capa_val)
            if color is not None:
                conn.set_last_entity_props(color=color)
            elif capa:
                conn.set_last_entity_props(layer=capa, color=256)
            return {"ok": True, "data": result}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="insertar_texto")
    def tool_insertar_texto(
        texto: str, x: float, y: float, altura: float = 2.5, rotacion: float = 0.0
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {
                "ok": True,
                "data": conn.add_text(texto, x, y, altura, rotacion=rotacion),
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
