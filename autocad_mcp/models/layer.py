from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LayerSpec:
    name: str
    color: int
    linetype: str
    lineweight: int


@dataclass(frozen=True)
class LayerInfo:
    nombre: str
    color: int
    linetype: str
    activa: bool
    congelada: bool
    bloqueada: bool
