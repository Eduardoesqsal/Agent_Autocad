from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntityRecord:
    tipo: str
    layer: str
    datos: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"tipo": self.tipo, "layer": self.layer, **self.datos}
