from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="obtener_capas")
    def obtener_capas() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.list_layers()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="cargar_tipo_linea")
    def tool_cargar_tipo_linea(nombre: str, archivo: str = "acad.lin") -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.load_linetype(nombre, archivo)}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="crear_capa")
    def tool_crear_capa(
        nombre: str,
        color: int | None = None,
        linetype: str | None = None,
        lineweight: int | None = None,
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {
                "ok": True,
                "data": conn.ensure_layer(
                    nombre, color=color, linetype=linetype, lineweight=lineweight
                ),
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="asignar_capa_entidad")
    def tool_asignar_capa_entidad(tipo: str, nombre_capa: str) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            conn.ensure_layer(nombre_capa)
            modificados = conn.set_entities_layer_by_type(tipo, nombre_capa)
            return {
                "ok": True,
                "modificados": len(modificados),
                "detalles": modificados,
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="asignar_capa_ultima_entidad")
    def tool_asignar_capa_ultima_entidad(
        capa: str, color_por_capa: bool = True
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            conn.ensure_layer(capa)
            color = 256 if color_por_capa else None
            result = conn.set_last_entity_props(layer=capa, color=color)
            return {"ok": True, "data": result}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
