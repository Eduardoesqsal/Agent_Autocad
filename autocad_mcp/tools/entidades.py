from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.tools._common import connected


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="listar_entidades")
    def tool_listar_entidades() -> dict:
        return connected(lambda conn: conn.list_entities())

    @mcp.tool(name="info_ultima_entidad")
    def tool_info_ultima_entidad() -> dict:
        return connected(lambda conn: conn.get_last_entity_info())

    @mcp.tool(name="info_entidad")
    def tool_info_entidad(handle: str) -> dict:
        return connected(lambda conn: conn.get_entity_info(handle))

    @mcp.tool(name="borrar_entidad")
    def tool_borrar_entidad(handle: str) -> dict:
        return connected(lambda conn: conn.delete_entity(handle))

    @mcp.tool(name="borrar_ultima_entidad")
    def tool_borrar_ultima_entidad() -> dict:
        return connected(lambda conn: conn.delete_last_entity())

    @mcp.tool(name="mover_ultima_entidad")
    def tool_mover_ultima_entidad(dx: float, dy: float) -> dict:
        return connected(lambda conn: conn.move_last_entity(dx, dy))

    @mcp.tool(name="copiar_ultima_entidad")
    def tool_copiar_ultima_entidad(dx: float, dy: float) -> dict:
        return connected(lambda conn: conn.copy_last_entity(dx, dy))

    @mcp.tool(name="rotar_ultima_entidad")
    def tool_rotar_ultima_entidad(angulo: float, cx: float = 0, cy: float = 0) -> dict:
        return connected(lambda conn: conn.rotate_last_entity(angulo, cx, cy))

    @mcp.tool(name="asignar_color_ultima_entidad")
    def tool_asignar_color_ultima_entidad(color: int) -> dict:
        return connected(lambda conn: conn.set_last_entity_props(color=color))

    @mcp.tool(name="asignar_props_entidad")
    def tool_asignar_props_entidad(
        handle: str, capa: str | None = None, color: int | None = None
    ) -> dict:
        return connected(
            lambda conn: conn.set_entity_props(handle, layer=capa, color=color)
        )
