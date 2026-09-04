from __future__ import annotations

from autocad_mcp.drawings.base import BasePlan
from autocad_mcp.models import LayerSpec


class FrontElevation(BasePlan):
    def __init__(
        self,
        origin_x: float = 0.0,
        origin_y: float = 0.0,
        ancho: float = 10.8,
        altura_muro: float = 3.0,
        altura_loseta: float = 0.3,
    ) -> None:
        super().__init__(origin_x, origin_y)
        self._ancho = ancho
        self._altura_muro = altura_muro
        self._altura_loseta = altura_loseta

    @property
    def layers(self) -> tuple[LayerSpec, ...]:
        return (
            LayerSpec("E_MUROS", 7, "Continuous", 50),
            LayerSpec("E_LOSA", 140, "Continuous", 35),
            LayerSpec("E_VENTANAS", 4, "Continuous", 25),
            LayerSpec("E_PUERTAS", 3, "Continuous", 25),
            LayerSpec("E_TERRENO", 94, "Continuous", 13),
            LayerSpec("E_COTAS", 2, "Continuous", 13),
            LayerSpec("E_TEXTOS", 7, "Continuous", 13),
            LayerSpec("E_EJES", 1, "Center", 13),
            LayerSpec("E_HACHURAS", 9, "Continuous", 13),
        )

    def _build_geometry(self) -> None:
        ox, oy = self.ox, self.oy
        ancho = self._ancho
        altura_muro = self._altura_muro
        altura_loseta = self._altura_loseta
        altura_total = altura_muro + altura_loseta
        suelo = oy

        self._l(ox - 1.0, suelo, ox + ancho + 1.0, suelo, "E_TERRENO")

        for i in range(int(ancho * 3)):
            x_pos = ox - 0.5 + i * 0.25
            if x_pos <= ox + ancho + 0.5:
                self._l(x_pos, suelo - 0.3, x_pos + 0.15, suelo, "E_HACHURAS")

        self._r(ox, suelo, ox + ancho, suelo + altura_total, "E_MUROS")

        self._r(
            ox - 0.3,
            suelo + altura_muro,
            ox + ancho + 0.3,
            suelo + altura_total,
            "E_LOSA",
        )

        for i in range(int(ancho * 4)):
            x_pos = ox - 0.2 + i * 0.15
            if x_pos <= ox + ancho + 0.2:
                self._l(
                    x_pos,
                    suelo + altura_muro + 0.05,
                    x_pos + 0.05,
                    suelo + altura_total - 0.05,
                    "E_HACHURAS",
                )

        self._l(ox, suelo - 0.5, ox, suelo + altura_total + 0.5, "E_EJES")
        self._l(
            ox + ancho, suelo - 0.5, ox + ancho, suelo + altura_total + 0.5, "E_EJES"
        )

        win_sill = 1.0
        win_height = 1.2
        windows = [
            (ox + 0.8, ox + 2.2),
            (ox + 3.8, ox + 5.6),
            (ox + 7.8, ox + 9.8),
        ]
        for x1, x2 in windows:
            self._r(
                x1, suelo + win_sill, x2, suelo + win_sill + win_height, "E_VENTANAS"
            )
            mid_y = suelo + win_sill + win_height / 2.0
            self._l(x1, mid_y, x2, mid_y, "E_VENTANAS")

        door_width = 0.9
        door_height = 2.1
        door_x = ox + 3.0
        self._r(door_x, suelo, door_x + door_width, suelo + door_height, "E_PUERTAS")
        self._l(
            door_x + 0.1,
            suelo + 0.3,
            door_x + 0.1,
            suelo + door_height - 0.1,
            "E_PUERTAS",
        )
        self._l(
            door_x + door_width - 0.1,
            suelo + 0.3,
            door_x + door_width - 0.1,
            suelo + door_height - 0.1,
            "E_PUERTAS",
        )

        dim_left = ox - 1.5
        dim_offset = 0.4
        dims = [
            (suelo, suelo + win_sill, "N.P. +1.00"),
            (suelo + win_sill, suelo + win_sill + win_height, "V=1.20"),
            (suelo, suelo + door_height, "P.TA +2.10"),
            (suelo + win_sill + win_height, suelo + altura_muro, ""),
            (suelo, suelo + altura_muro, "H=3.00"),
        ]
        for y1, y2, label in dims:
            self._l(dim_left, y1, dim_left - dim_offset, y1, "E_COTAS")
            self._l(dim_left, y2, dim_left - dim_offset, y2, "E_COTAS")
            self._l(dim_left - dim_offset, y1, dim_left - dim_offset, y2, "E_COTAS")
            if label:
                self._t(label, dim_left - 1.2, (y1 + y2) / 2.0 - 0.08, "E_TEXTOS")

        self._t(
            "ALZADO FRONTAL",
            ox + ancho / 2.0 - 1.5,
            suelo + altura_total + 0.6,
            "E_TEXTOS",
        )
        self._t(
            f"ANCHO: {ancho:.2f} m  |  ALTURA: {altura_muro:.2f} m  |  LOSA: {altura_loseta:.2f} m",
            ox + ancho / 2.0 - 3.5,
            suelo + altura_total + 0.25,
            "E_TEXTOS",
        )
        self._t("A", ox - 0.08, suelo - 0.7, "E_EJES")
        self._t("B", ox + ancho - 0.08, suelo - 0.7, "E_EJES")

    def draw(self) -> dict:
        result = super().draw()
        result.update(
            {
                "tipo": "alzado_frontal",
                "ancho_m": self._ancho,
                "altura_muro_m": self._altura_muro,
                "altura_total_m": round(self._altura_muro + self._altura_loseta, 2),
                "capas": [s.name for s in self.layers],
            }
        )
        return result
