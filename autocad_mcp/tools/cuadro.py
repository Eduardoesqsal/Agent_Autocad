from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.application import ConstructionTableService
from autocad_mcp.tools._common import run_tool


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="cuadro_construccion")
    def tool_cuadro_construccion(
        colindantes: list[str] | None = None,
        altura_texto: float = 0.6,
        escala_header: float = 1.0,
        escala_area: float = 1.0,
    ) -> dict:
        return run_tool(
            lambda conn: ConstructionTableService(conn).create_construction_table(
                colindantes, altura_texto, escala_header, escala_area
            )
        )

    @mcp.tool(name="cuadro_curvas")
    def tool_cuadro_curvas() -> dict:
        return run_tool(
            lambda conn: ConstructionTableService(conn).create_curve_table()
        )

    @mcp.tool(name="reticula_utm")
    def tool_reticula_utm(espaciado: float, tamanio_cruz: float | None = None) -> dict:
        return run_tool(
            lambda conn: ConstructionTableService(conn).create_utm_grid(
                espaciado, tamanio_cruz
            )
        )
