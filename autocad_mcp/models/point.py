from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float

    def __iter__(self):
        return iter((self.x, self.y))
