from __future__ import annotations

from typing import Any

from autocad_mcp.core.autocad import AutoCADConnection
from autocad_mcp.models import LayerSpec


class LayerManager:
    def __init__(self, conn: AutoCADConnection) -> None:
        self._conn = conn

    def ensure_layers(self, specs: tuple[LayerSpec, ...]) -> list[dict[str, Any]]:
        return [
            self._conn.ensure_layer(
                s.name, color=s.color, linetype=s.linetype, lineweight=s.lineweight
            )
            for s in specs
        ]

    def list_all(self) -> list[dict[str, Any]]:
        return self._conn.list_layers()

    def create(self, nombre: str) -> dict[str, Any]:
        return self._conn.ensure_layer(nombre)

    def find(self, nombre: str) -> Any | None:
        return self._conn.find_layer(nombre)
