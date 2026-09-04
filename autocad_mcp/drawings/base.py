from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from autocad_mcp.core.autocad import AutoCADConnection
from autocad_mcp.models import LayerSpec


class BasePlan(ABC):
    def __init__(self, origin_x: float = 0.0, origin_y: float = 0.0) -> None:
        self.ox = origin_x
        self.oy = origin_y
        self._cad = AutoCADConnection.get_instance()
        self._rec: list[dict[str, Any]] = []

    @property
    @abstractmethod
    def layers(self) -> tuple[LayerSpec, ...]: ...

    @abstractmethod
    def _build_geometry(self) -> None: ...

    def _init_layers(self) -> None:
        for spec in self.layers:
            self._cad.ensure_layer(
                spec.name,
                color=spec.color,
                linetype=spec.linetype,
                lineweight=spec.lineweight,
            )

    def _r(self, x1: float, y1: float, x2: float, y2: float, layer: str) -> None:
        self._rec.append(self._cad.add_rectangle(x1, y1, x2, y2, layer))

    def _l(self, x1: float, y1: float, x2: float, y2: float, layer: str) -> None:
        self._rec.append(self._cad.add_line(x1, y1, x2, y2, layer))

    def _c(self, x: float, y: float, r: float, layer: str) -> None:
        self._rec.append(self._cad.add_circle(x, y, r, layer))

    def _t(self, txt: str, x: float, y: float, layer: str, h: float = 0.18) -> None:
        self._rec.append(self._cad.add_text(txt, x, y, h, layer))

    def _tr(
        self, txt: str, x: float, y: float, ang: float, layer: str, h: float = 0.18
    ) -> None:
        self._rec.append(self._cad.add_text(txt, x, y, h, layer, rotacion=ang))

    def _a(
        self, x: float, y: float, r: float, a1: float, a2: float, layer: str
    ) -> None:
        self._rec.append(self._cad.add_arc(x, y, r, a1, a2, layer))

    def _hatch_rect(
        self, x1: float, y1: float, x2: float, y2: float, layer: str
    ) -> None:
        step = 0.15
        p = x1 - (y2 - y1)
        while p <= x2:
            xs = max(x1, p)
            ys = y1 + max(0.0, x1 - p)
            xe = min(x2, p + (y2 - y1))
            ye = y2 - max(0.0, p + (y2 - y1) - x2)
            if xs < xe:
                self._l(xs, ys, xe, ye, layer)
            p += step

    def _wall_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        t: float,
        wall_layer: str,
        hatch_layer: str,
    ) -> None:
        self._l(x1, y1, x2, y2, wall_layer)
        dx, dy = 0.0, 0.0
        if abs(x2 - x1) > abs(y2 - y1):
            dy = t
        else:
            dx = t
        self._l(x1 + dx, y1 + dy, x2 + dx, y2 + dy, wall_layer)
        self._hatch_rect(
            min(x1, x2), min(y1, y2), max(x1, x2) + dx, max(y1, y2) + dy, hatch_layer
        )

    def _wall_rect(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        wall_layer: str,
        hatch_layer: str,
    ) -> None:
        self._r(x1, y1, x2, y2, wall_layer)
        self._hatch_rect(x1 + 0.02, y1 + 0.02, x2 - 0.02, y2 - 0.02, hatch_layer)

    def _door(
        self,
        x: float,
        y: float,
        w: float,
        orient: str,
        side: str,
        door_layer: str,
        swing_layer: str,
    ) -> None:
        if orient == "h":
            self._l(x, y, x + w, y, door_layer)
            self._l(x, y, x, y + w * 0.06, door_layer)
            if side == "up":
                self._a(x, y, w, 0, 90, swing_layer)
                self._l(x, y, x + w, y + w, swing_layer)
            else:
                self._a(x, y, w, 270, 360, swing_layer)
                self._l(x, y, x + w, y - w, swing_layer)
        else:
            self._l(x, y, x, y + w, door_layer)
            self._l(x, y, x + w * 0.06, y, door_layer)
            if side == "r":
                self._a(x, y, w, 0, 90, swing_layer)
                self._l(x, y, x + w, y + w, swing_layer)
            else:
                self._a(x, y, w, 90, 180, swing_layer)
                self._l(x, y, x - w, y + w, swing_layer)

    def _win(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        win_layer: str,
        glaz_layer: str,
    ) -> None:
        self._l(x1, y1, x2, y2, win_layer)
        dx, dy = x2 - x1, y2 - y1
        if abs(dx) >= abs(dy):
            self._l(x1, y1 + 0.06, x2, y2 + 0.06, win_layer)
            self._l(x1, y1 + 0.12, x2, y2 + 0.12, glaz_layer)
        else:
            self._l(x1 + 0.06, y1, x2 + 0.06, y2, win_layer)
            self._l(x1 + 0.12, y1, x2 + 0.12, y2, glaz_layer)

    def _dim_h(
        self, x: float, y: float, w: float, dim_layer: str, label: str = ""
    ) -> None:
        self._l(x, y, x + w, y, dim_layer)
        self._l(x, y - 0.08, x, y + 0.08, dim_layer)
        self._l(x + w, y - 0.08, x + w, y + 0.08, dim_layer)
        txt = label if label else f"{w:.2f}"
        self._t(txt, x + w / 2 - 0.20, y + 0.10, dim_layer, 0.10)

    def _dim_v(
        self, x: float, y: float, h: float, dim_layer: str, label: str = ""
    ) -> None:
        self._l(x, y, x, y + h, dim_layer)
        self._l(x - 0.08, y, x + 0.08, y, dim_layer)
        self._l(x - 0.08, y + h, x + 0.08, y + h, dim_layer)
        txt = label if label else f"{h:.2f}"
        self._t(txt, x + 0.12, y + h / 2 - 0.06, dim_layer, 0.10)

    def _arrow_north(self, x: float, y: float, layer: str, text_layer: str) -> None:
        self._l(x, y - 0.5, x, y + 1.5, layer)
        self._l(x, y + 1.5, x - 0.4, y + 0.7, layer)
        self._l(x, y + 1.5, x + 0.4, y + 0.7, layer)
        self._t("N", x - 0.15, y + 1.7, text_layer, 0.35)

    def draw(self) -> dict[str, Any]:
        self._cad.connect()
        self._init_layers()
        self._build_geometry()
        self._cad.zoom_extents()
        return {
            "tipo": self.__class__.__name__,
            "origen": {"x": self.ox, "y": self.oy},
            "entidades": self._rec,
        }
