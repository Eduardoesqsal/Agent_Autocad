from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="generar_lotes")
    def tool_generar_lotes(
        cantidad: int = 90,
        x_inicio: float = 2881.522,
        y_inicio: float = 2062.1257,
        ancho: float = 10.0,
        alto: float = 20.0,
        separacion: float = 80.0,
        capa_lotes: str = "lotes",
        capa_solapa: str = "solapa",
        altura_texto: float = 2.5,
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            conn.ensure_layer(capa_lotes, color=1)
            conn.ensure_layer(capa_solapa, color=7)

            lotes: list[dict] = []
            total_rect = 0
            total_text = 0

            for i in range(cantidad):
                x0 = x_inicio + i * separacion
                x1 = x0 + ancho
                y1 = y_inicio + alto
                rect = conn.add_rectangle(x0, y_inicio, x1, y1, layer=capa_lotes)
                conn.set_last_entity_props(layer=capa_lotes, color=256)
                lotes.append(rect)
                total_rect += 1

                cx = (x0 + x1) / 2.0
                cy = (y_inicio + y1) / 2.0
                texto = f"LOTE {i + 1}"
                txt = conn.add_text(
                    texto, cx, cy, altura=altura_texto, layer=capa_solapa
                )
                conn.set_last_entity_props(layer=capa_solapa, color=256)
                lotes.append(txt)
                total_text += 1

            return {
                "ok": True,
                "data": {
                    "cantidad": cantidad,
                    "rectangulos": total_rect,
                    "textos": total_text,
                    "entidades": lotes,
                },
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
