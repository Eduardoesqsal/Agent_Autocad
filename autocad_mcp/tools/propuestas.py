from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.drawings import ArchitecturalProposals
from autocad_mcp.core.autocad import AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="generar_propuestas")
    def tool_generar_propuestas(
        prompt: str | None = None, autolaunch: bool | None = None
    ) -> dict:
        try:
            plan = ArchitecturalProposals()
            return plan.draw(prompt=prompt)
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
