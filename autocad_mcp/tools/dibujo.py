from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="obtener_dibujo_activo")
    def tool_obtener_dibujo_activo() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.get_active_drawing_info()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="guardar_dwg")
    def tool_guardar_dwg() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.save_dwg()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="contar_entidades")
    def tool_contar_entidades() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.count_entities()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="zoom_extensiones")
    def tool_zoom_extensiones() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            conn.zoom_extents()
            return {"ok": True, "mensaje": "Zoom Extents ejecutado."}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="diagnosticar_conexion_autocad")
    def tool_diagnosticar_conexion_autocad() -> dict:
        try:
            return {"ok": True, "data": AutoCADConnection.diagnosticar()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
