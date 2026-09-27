from __future__ import annotations

from typing import Any

from autocad_mcp.config import DEFAULT_LAYERS
from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError
from autocad_mcp.core.geometry import (
    angle,
    distance,
    get_polyline_vertices,
    midpoint,
    perpendicular_offset,
)


class AnnotationService:
    def __init__(self, conn: AutoCADConnection) -> None:
        self._conn = conn

    def annotate_distances(self, altura: float = 2.5) -> dict[str, Any]:
        anotaciones: list[dict[str, Any]] = []
        text_layer = "ANOTACIONES"
        self._conn.ensure_layer(text_layer, color=DEFAULT_LAYERS[text_layer])

        for ent in AutoCADConnection._iter_collection_items(self._conn.model_space):
            tipo = str(getattr(ent, "ObjectName", ""))
            handle = str(getattr(ent, "Handle", ""))
            if "AcDbLine" in tipo:
                anotaciones.append(self._annotate_line(ent, handle, altura, text_layer))
            elif "AcDbPolyline" in tipo or "AcDb3dPolyline" in tipo:
                label = (
                    "3DPolilinea segmento"
                    if "AcDb3dPolyline" in tipo
                    else "Polilinea segmento"
                )
                anotaciones.extend(
                    self._annotate_polyline(ent, handle, altura, text_layer, label)
                )

        self._conn.zoom_extents()
        return {"ok": True, "anotaciones": len(anotaciones), "detalles": anotaciones}

    def annotate_adjoining(
        self,
        colindantes: list[str],
        capa: str = "COLINDANTES",
        altura: float = 2.0,
        separacion: float = 10.0,
    ) -> dict[str, Any]:
        self._conn.ensure_layer(capa, color=DEFAULT_LAYERS.get(capa.upper(), 7))
        poly_handle, vertices = self._last_polyline_vertices()

        if len(vertices) < 3:
            return {"ok": False, "error": "La polilinea debe tener al menos 3 vertices."}

        segments = len(vertices) - 1
        if len(colindantes) != segments:
            return {
                "ok": False,
                "error": (
                    f"La polilinea tiene {segments} lados, pero se proporcionaron "
                    f"{len(colindantes)} colindantes."
                ),
            }

        signed_area = sum(
            vertices[i][0] * vertices[i + 1][1]
            - vertices[i + 1][0] * vertices[i][1]
            for i in range(segments)
        )
        clockwise = signed_area < 0

        resultados: list[dict[str, Any]] = []
        for i in range(segments):
            x1, y1 = vertices[i]
            x2, y2 = vertices[i + 1]
            mx, my = midpoint(x1, y1, x2, y2)
            rot = angle(x1, y1, x2, y2)
            ox, oy = perpendicular_offset(
                x1, y1, x2, y2, separacion, outward=clockwise
            )
            result = self._conn.add_text(
                str(colindantes[i]),
                mx + ox,
                my + oy,
                altura,
                layer=capa,
                rotacion=rot,
            )
            resultados.append(
                {
                    "lado": i + 1,
                    "colindante": str(colindantes[i]),
                    "handle": result.get("handle", ""),
                    "angulo": round(rot, 3),
                }
            )

        self._conn.zoom_extents()
        return {
            "ok": True,
            "colindantes": len(resultados),
            "poligono_handle": poly_handle,
            "detalles": resultados,
        }

    def _annotate_line(
        self, ent: Any, handle: str, altura: float, text_layer: str
    ) -> dict[str, Any]:
        sp = ent.StartPoint
        ep = ent.EndPoint
        x1, y1 = float(sp[0]), float(sp[1])
        x2, y2 = float(ep[0]), float(ep[1])
        dist = distance(x1, y1, x2, y2)
        mx, my = midpoint(x1, y1, x2, y2)
        rot = angle(x1, y1, x2, y2)
        texto = f"{dist:.2f}"
        self._conn.add_text(texto, mx, my, altura, layer=text_layer, rotacion=rot)
        return {
            "entidad": handle,
            "tipo": "Linea",
            "distancia": round(dist, 2),
            "texto": texto,
        }

    def _annotate_polyline(
        self,
        ent: Any,
        handle: str,
        altura: float,
        text_layer: str,
        segment_label: str,
    ) -> list[dict[str, Any]]:
        anotaciones: list[dict[str, Any]] = []
        vertices = get_polyline_vertices(ent)
        for i in range(len(vertices) - 1):
            x1, y1 = vertices[i]
            x2, y2 = vertices[i + 1]
            dist = distance(x1, y1, x2, y2)
            mx, my = midpoint(x1, y1, x2, y2)
            rot = angle(x1, y1, x2, y2)
            texto = f"{dist:.2f}"
            self._conn.add_text(texto, mx, my, altura, layer=text_layer, rotacion=rot)
            anotaciones.append(
                {
                    "entidad": handle,
                    "tipo": segment_label,
                    "indice": i,
                    "distancia": round(dist, 2),
                    "texto": texto,
                }
            )
        return anotaciones

    def _last_polyline_vertices(self) -> tuple[str, list[tuple[float, float]]]:
        entities = AutoCADConnection._iter_collection_items(self._conn.model_space)
        for ent in reversed(entities):
            obj_name = str(getattr(ent, "ObjectName", ""))
            if "AcDbPolyline" in obj_name or "AcDb3dPolyline" in obj_name:
                return str(getattr(ent, "Handle", "")), get_polyline_vertices(ent)
        raise AutoCADError("No se encontro ninguna polilinea en el dibujo.")

