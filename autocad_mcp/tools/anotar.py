from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.application import AnnotationService
from autocad_mcp.tools._common import run_tool


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="anotar_distancias")
    def tool_anotar_distancias(altura: float = 2.5) -> dict:
        return run_tool(lambda conn: AnnotationService(conn).annotate_distances(altura))

    @mcp.tool(name="anotar_colindantes")
    def tool_anotar_colindantes(
        colindantes: list[str],
        capa: str = "COLINDANTES",
        altura: float = 2.0,
        separacion: float = 10.0,
    ) -> dict:
        return run_tool(
            lambda conn: AnnotationService(conn).annotate_adjoining(
                colindantes, capa, altura, separacion
            )
        )
