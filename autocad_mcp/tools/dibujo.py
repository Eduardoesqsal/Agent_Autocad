from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection
from autocad_mcp.tools._common import connected, run_tool


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="obtener_dibujo_activo")
    def tool_obtener_dibujo_activo() -> dict:
        return connected(lambda conn: conn.get_active_drawing_info())

    @mcp.tool(name="guardar_dwg")
    def tool_guardar_dwg() -> dict:
        return connected(lambda conn: conn.save_dwg())

    @mcp.tool(name="contar_entidades")
    def tool_contar_entidades() -> dict:
        return connected(lambda conn: conn.count_entities())

    @mcp.tool(name="zoom_extensiones")
    def tool_zoom_extensiones() -> dict:
        def zoom(conn):
            conn.zoom_extents()
            return {"ok": True, "mensaje": "Zoom Extents ejecutado."}

        return run_tool(zoom)

    @mcp.tool(name="diagnosticar_conexion_autocad")
    def tool_diagnosticar_conexion_autocad() -> dict:
        return {"ok": True, "data": AutoCADConnection.diagnosticar()}
