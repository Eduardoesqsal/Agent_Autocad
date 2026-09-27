from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.tools._common import connected, run_tool


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="obtener_capas")
    def obtener_capas() -> dict:
        return connected(lambda conn: conn.list_layers())

    @mcp.tool(name="cargar_tipo_linea")
    def tool_cargar_tipo_linea(nombre: str, archivo: str = "acad.lin") -> dict:
        return connected(lambda conn: conn.load_linetype(nombre, archivo))

    @mcp.tool(name="crear_capa")
    def tool_crear_capa(
        nombre: str,
        color: int | None = None,
        linetype: str | None = None,
        lineweight: int | None = None,
    ) -> dict:
        return connected(
            lambda conn: conn.ensure_layer(
                nombre, color=color, linetype=linetype, lineweight=lineweight
            )
        )

    @mcp.tool(name="asignar_capa_entidad")
    def tool_asignar_capa_entidad(tipo: str, nombre_capa: str) -> dict:
        def assign(conn):
            conn.ensure_layer(nombre_capa)
            modificados = conn.set_entities_layer_by_type(tipo, nombre_capa)
            return {
                "ok": True,
                "modificados": len(modificados),
                "detalles": modificados,
            }

        return run_tool(assign)

    @mcp.tool(name="asignar_capa_ultima_entidad")
    def tool_asignar_capa_ultima_entidad(
        capa: str, color_por_capa: bool = True
    ) -> dict:
        def assign(conn):
            conn.ensure_layer(capa)
            color = 256 if color_por_capa else None
            return conn.set_last_entity_props(layer=capa, color=color)

        return connected(assign)
