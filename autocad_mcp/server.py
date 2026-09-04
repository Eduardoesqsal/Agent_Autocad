from __future__ import annotations

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise RuntimeError(
        "FastMCP is required. Install dependencies with `pip install -r requirements.txt`."
    ) from exc

from autocad_mcp.tools.capas import register_tools as register_layer_tools
from autocad_mcp.tools.dibujo import register_tools as register_drawing_tools
from autocad_mcp.tools.geometria import register_tools as register_geometry_tools
from autocad_mcp.tools.bloques import register_tools as register_block_tools
from autocad_mcp.tools.propuestas import register_tools as register_architecture_tools
from autocad_mcp.tools.alzado import register_tools as register_elevation_tools
from autocad_mcp.tools.casa import register_tools as register_americana_tools
from autocad_mcp.tools.plano_topo import register_tools as register_topo_tools
from autocad_mcp.tools.planta import register_tools as register_pro_arch_tools
from autocad_mcp.tools.planta_bloques import register_tools as register_bloques_tools
from autocad_mcp.tools.cuadro import register_tools as register_cuadro_tools
from autocad_mcp.tools.anotar import register_tools as register_anotar_tools
from autocad_mcp.tools.entidades import register_tools as register_entity_tools
from autocad_mcp.tools.lotes import register_tools as register_lotes_tools

mcp = FastMCP("autocad_mcp")
register_layer_tools(mcp)
register_drawing_tools(mcp)
register_geometry_tools(mcp)
register_block_tools(mcp)
register_architecture_tools(mcp)
register_elevation_tools(mcp)
register_americana_tools(mcp)
register_topo_tools(mcp)
register_pro_arch_tools(mcp)
register_bloques_tools(mcp)
register_cuadro_tools(mcp)
register_anotar_tools(mcp)
register_entity_tools(mcp)
register_lotes_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
