from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError
from autocad_mcp.core.geometry import (
    distance,
    midpoint,
    angle,
    perpendicular_offset,
    get_polyline_vertices,
)


def _iter_entities(conn: AutoCADConnection) -> list[Any]:
    return AutoCADConnection._iter_collection_items(conn.model_space)


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="anotar_distancias")
    def tool_anotar_distancias(altura: float = 2.5) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()

            anotaciones: list[dict[str, Any]] = []
            entities = _iter_entities(conn)
            text_layer = "ANOTACIONES"

            conn.ensure_layer(text_layer, color=2)

            for ent in entities:
                tipo = str(getattr(ent, "ObjectName", ""))
                handle = str(getattr(ent, "Handle", ""))

                if "AcDbLine" in tipo:
                    sp = ent.StartPoint
                    ep = ent.EndPoint
                    x1, y1 = float(sp[0]), float(sp[1])
                    x2, y2 = float(ep[0]), float(ep[1])
                    dist = distance(x1, y1, x2, y2)
                    mx, my = midpoint(x1, y1, x2, y2)
                    rot = angle(x1, y1, x2, y2)
                    texto = f"{dist:.2f}"
                    conn.add_text(texto, mx, my, altura, layer=text_layer, rotacion=rot)
                    anotaciones.append(
                        {
                            "entidad": handle,
                            "tipo": "Linea",
                            "distancia": round(dist, 2),
                            "texto": texto,
                        }
                    )

                elif "AcDbPolyline" in tipo:
                    vertices = get_polyline_vertices(ent)
                    for i in range(len(vertices) - 1):
                        x1, y1 = vertices[i]
                        x2, y2 = vertices[i + 1]
                        dist = distance(x1, y1, x2, y2)
                        mx, my = midpoint(x1, y1, x2, y2)
                        rot = angle(x1, y1, x2, y2)
                        texto = f"{dist:.2f}"
                        conn.add_text(
                            texto, mx, my, altura, layer=text_layer, rotacion=rot
                        )
                        anotaciones.append(
                            {
                                "entidad": handle,
                                "tipo": "Polilinea segmento",
                                "indice": i,
                                "distancia": round(dist, 2),
                                "texto": texto,
                            }
                        )

                elif "AcDb3dPolyline" in tipo:
                    vertices = get_polyline_vertices(ent)
                    for i in range(len(vertices) - 1):
                        x1, y1 = vertices[i]
                        x2, y2 = vertices[i + 1]
                        dist = distance(x1, y1, x2, y2)
                        mx, my = midpoint(x1, y1, x2, y2)
                        rot = angle(x1, y1, x2, y2)
                        texto = f"{dist:.2f}"
                        conn.add_text(
                            texto, mx, my, altura, layer=text_layer, rotacion=rot
                        )
                        anotaciones.append(
                            {
                                "entidad": handle,
                                "tipo": "3DPolilinea segmento",
                                "indice": i,
                                "distancia": round(dist, 2),
                                "texto": texto,
                            }
                        )

            conn.zoom_extents()
            return {
                "ok": True,
                "anotaciones": len(anotaciones),
                "detalles": anotaciones,
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="anotar_colindantes")
    def tool_anotar_colindantes(
        colindantes: list[str],
        capa: str = "colindantes",
        altura: float = 2.0,
        separacion: float = 10.0,
    ) -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()

            conn.ensure_layer(capa, color=7)
            entities = _iter_entities(conn)
            poly_handle = None
            vertices = None

            for ent in reversed(entities):
                obj_name = str(getattr(ent, "ObjectName", ""))
                if "AcDbPolyline" in obj_name or "AcDb3dPolyline" in obj_name:
                    poly_handle = str(getattr(ent, "Handle", ""))
                    vertices = get_polyline_vertices(ent)
                    break

            if vertices is None or poly_handle is None:
                return {
                    "ok": False,
                    "error": "No se encontro ninguna polilinea en el dibujo.",
                }

            if len(vertices) < 3:
                return {
                    "ok": False,
                    "error": "La polilinea debe tener al menos 3 vertices.",
                }

            segments = len(vertices) - 1
            if len(colindantes) != segments:
                return {
                    "ok": False,
                    "error": f"La polilinea tiene {segments} lados, pero se proporcionaron {len(colindantes)} colindantes.",
                }

            signed_area = 0.0
            for i in range(segments):
                x1, y1 = vertices[i]
                x2, y2 = vertices[i + 1]
                signed_area += x1 * y2 - x2 * y1

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
                tx, ty = mx + ox, my + oy

                result = conn.add_text(
                    str(colindantes[i]),
                    tx,
                    ty,
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

            conn.zoom_extents()
            return {
                "ok": True,
                "colindantes": len(resultados),
                "poligono_handle": poly_handle,
                "detalles": resultados,
            }
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
