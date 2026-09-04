from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="listar_entidades")
    def tool_listar_entidades() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.list_entities()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="info_ultima_entidad")
    def tool_info_ultima_entidad() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.get_last_entity_info()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="info_entidad")
    def tool_info_entidad(handle: str) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.get_entity_info(handle)}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="borrar_entidad")
    def tool_borrar_entidad(handle: str) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.delete_entity(handle)}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="borrar_ultima_entidad")
    def tool_borrar_ultima_entidad() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.delete_last_entity()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="mover_ultima_entidad")
    def tool_mover_ultima_entidad(dx: float, dy: float) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.move_last_entity(dx, dy)}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="copiar_ultima_entidad")
    def tool_copiar_ultima_entidad(dx: float, dy: float) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.copy_last_entity(dx, dy)}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="rotar_ultima_entidad")
    def tool_rotar_ultima_entidad(angulo: float, cx: float = 0, cy: float = 0) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.rotate_last_entity(angulo, cx, cy)}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="asignar_color_ultima_entidad")
    def tool_asignar_color_ultima_entidad(color: int) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.set_last_entity_props(color=color)}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="asignar_props_entidad")
    def tool_asignar_props_entidad(
        handle: str, capa: str | None = None, color: int | None = None
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {
                "ok": True,
                "data": conn.set_entity_props(handle, layer=capa, color=color),
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
