from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.application import GeometryService
from autocad_mcp.tools._common import connected


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
        return connected(
            lambda conn: GeometryService(conn).create_line(
                x1, y1, x2, y2, layer=capa, color=color
            )
        )

    @mcp.tool(name="crear_circulo")
    def tool_crear_circulo(
        x: float,
        y: float,
        radio: float,
        capa: str | None = None,
        color: int | None = None,
    ) -> dict:
        return connected(
            lambda conn: GeometryService(conn).create_circle(
                x, y, radio, layer=capa, color=color
            )
        )

    @mcp.tool(name="crear_polilinea")
    def tool_crear_polilinea(
        puntos: list,
        cerrar: bool = False,
        capa: str | None = None,
        color: int | None = None,
    ) -> dict:
        return connected(
            lambda conn: GeometryService(conn).create_polyline(
                puntos, cerrar=cerrar, layer=capa, color=color
            )
        )

    @mcp.tool(name="crear_poligono")
    def tool_crear_poligono(
        puntos: list, capa: str = "", color: int | None = None
    ) -> dict:
        return connected(
            lambda conn: GeometryService(conn).create_polygon(
                puntos, layer=capa or None, color=color
            )
        )

    @mcp.tool(name="insertar_texto")
    def tool_insertar_texto(
        texto: str, x: float, y: float, altura: float = 2.5, rotacion: float = 0.0
    ) -> dict:
        return connected(
            lambda conn: GeometryService(conn).insert_text(
                texto, x, y, altura, rotacion=rotacion
            )
        )
