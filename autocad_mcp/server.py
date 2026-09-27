from __future__ import annotations

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise RuntimeError(
        "FastMCP is required. Install dependencies with `pip install -r requirements.txt`."
    ) from exc

from autocad_mcp.config import MCP_SERVER_NAME
from autocad_mcp.tools.alzado import register_tools as register_elevation_tools
from autocad_mcp.tools.anotar import register_tools as register_anotar_tools
from autocad_mcp.tools.bloques import register_tools as register_block_tools
from autocad_mcp.tools.capas import register_tools as register_layer_tools
from autocad_mcp.tools.casa import register_tools as register_americana_tools
from autocad_mcp.tools.cuadro import register_tools as register_cuadro_tools
from autocad_mcp.tools.dibujo import register_tools as register_drawing_tools
from autocad_mcp.tools.entidades import register_tools as register_entity_tools
from autocad_mcp.tools.geometria import register_tools as register_geometry_tools
from autocad_mcp.tools.lotes import register_tools as register_lotes_tools
from autocad_mcp.tools.plano_topo import register_tools as register_topo_tools
from autocad_mcp.tools.planta import register_tools as register_pro_arch_tools
from autocad_mcp.tools.planta_bloques import register_tools as register_bloques_tools
from autocad_mcp.tools.propuestas import register_tools as register_architecture_tools

TOOL_REGISTRARS = (
    register_layer_tools,
    register_drawing_tools,
    register_geometry_tools,
    register_block_tools,
    register_architecture_tools,
    register_elevation_tools,
    register_americana_tools,
    register_topo_tools,
    register_pro_arch_tools,
    register_bloques_tools,
    register_cuadro_tools,
    register_anotar_tools,
    register_entity_tools,
    register_lotes_tools,
)


def create_app() -> FastMCP:
    app = FastMCP(MCP_SERVER_NAME)
    for register_tools in TOOL_REGISTRARS:
        register_tools(app)
    return app


mcp = create_app()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
