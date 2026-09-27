from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any


def load_local_env() -> None:
    env_path = os.path.join(os.path.dirname(__file__), ".env.local")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


load_local_env()

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")


SYSTEM_PROMPT = """
Eres un agente experto en AutoCAD 2021, dibujo arquitectonico, topografia y CAD.
Convierte instrucciones naturales del usuario en un plan JSON de acciones CAD.
No pidas que el usuario sea especifico si puedes inferir valores razonables.
Unidades por defecto: metros. Origen por defecto: 0,0. Capa por defecto: TERRENO.

Acciones permitidas:
- create_layers
- line: x1,y1,x2,y2,layer
- circle: x,y,radius,layer
- rectangle: x,y,width,height,layer
- polyline: points [[x,y],...], closed, layer
- regular_polygon: sides,radius,x,y,layer
- text: value,x,y,height,layer
- utm_grid: spacing
- architectural_plan
- dimension: x1,y1,x2,y2
- annotate_distances
- label_vertices
- move_last: dx,dy
- copy_last: dx,dy
- rotate_last: angle,cx,cy
- delete_last
- zoom
- save
- cad_command: command

Responde solo JSON con:
{
  "reply": "explicacion breve en espanol",
  "actions": [{"type":"...", ...}]
}
"""


def main() -> int:
    prompt = sys.stdin.read().strip()
    if not prompt:
        print(json.dumps({"reply": "No recibi prompt.", "actions": []}))
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            print(json.dumps(plan_with_openai(prompt, api_key), ensure_ascii=False))
            return 0
        except Exception as exc:  # noqa: BLE001 - CLI fallback must keep AutoCAD usable.
            fallback = local_plan(prompt)
            fallback["reply"] = f"Use razonamiento local porque fallo el agente OpenAI: {exc}. " + fallback["reply"]
            print(json.dumps(fallback, ensure_ascii=False))
            return 0

    print(json.dumps(local_plan(prompt), ensure_ascii=False))
    return 0


def plan_with_openai(prompt: str, api_key: str) -> dict[str, Any]:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "reply": {"type": "string"},
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": True,
                    "properties": {"type": {"type": "string"}},
                    "required": ["type"],
                },
            },
        },
        "required": ["reply", "actions"],
    }
    payload = {
        "model": MODEL,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "cad_plan",
                "schema": schema,
                "strict": False,
            }
        },
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(detail) from exc

    text = data.get("output_text")
    if not text:
        parts: list[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    parts.append(content.get("text", ""))
        text = "".join(parts)
    plan = json.loads(text)
    return sanitize_plan(plan)


def local_plan(prompt: str) -> dict[str, Any]:
    text = normalize(prompt)
    nums = numbers(prompt)
    actions: list[dict[str, Any]] = []

    if any_word(text, "plano arquitectonico", "planta arquitectonica", "casa", "vivienda", "normas"):
        return {"reply": "Generare una planta arquitectonica base con criterios normativos editables.", "actions": [{"type": "architectural_plan"}]}

    if any_word(text, "reticula", "utm", "grid"):
        actions.append({"type": "utm_grid", "spacing": nums[0] if nums else 10})
        return {"reply": "Generare reticula UTM.", "actions": actions}

    if any_word(text, "capa", "capas", "layers"):
        return {"reply": "Creare capas base.", "actions": [{"type": "create_layers"}]}

    if any_word(text, "zoom", "acercar", "encuadrar"):
        return {"reply": "Ejecutare zoom extents.", "actions": [{"type": "zoom"}]}

    if any_word(text, "guardar", "salvar"):
        return {"reply": "Guardare el dibujo.", "actions": [{"type": "save"}]}

    if any_word(text, "borrar", "eliminar") and any_word(text, "ultima", "ultimo"):
        return {"reply": "Borro la ultima entidad.", "actions": [{"type": "delete_last"}]}

    if any_word(text, "mover", "mueve") and nums:
        return {"reply": "Muevo la ultima entidad.", "actions": [{"type": "move_last", "dx": nums[0], "dy": nums[1] if len(nums) > 1 else 0}]}

    if any_word(text, "copiar", "copia") and nums:
        return {"reply": "Copio la ultima entidad.", "actions": [{"type": "copy_last", "dx": nums[0], "dy": nums[1] if len(nums) > 1 else 0}]}

    if any_word(text, "rotar", "rota") and nums:
        return {"reply": "Roto la ultima entidad.", "actions": [{"type": "rotate_last", "angle": nums[0], "cx": nums[1] if len(nums) > 2 else 0, "cy": nums[2] if len(nums) > 2 else 0}]}

    if any_word(text, "texto", "nota", "rotulo", "rótulo"):
        value = quoted(prompt) or "TEXTO"
        return {"reply": "Inserto texto.", "actions": [{"type": "text", "value": value, "x": nums[0] if len(nums) > 0 else 0, "y": nums[1] if len(nums) > 1 else 0, "height": nums[2] if len(nums) > 2 else 0.6, "layer": "NOTAS"}]}

    if any_word(text, "circulo", "circle", "redondo"):
        if len(nums) >= 3:
            action = {"type": "circle", "x": nums[0], "y": nums[1], "radius": nums[2], "layer": "TERRENO"}
        else:
            action = {"type": "circle", "x": 0, "y": 0, "radius": nums[0] if nums else 5, "layer": "TERRENO"}
        return {"reply": "Dibujo circulo inferido.", "actions": [action]}

    if any_word(text, "linea", "línea", "line"):
        if len(nums) >= 4:
            action = {"type": "line", "x1": nums[0], "y1": nums[1], "x2": nums[2], "y2": nums[3], "layer": "TERRENO"}
        else:
            action = {"type": "line", "x1": 0, "y1": 0, "x2": nums[0] if nums else 10, "y2": 0, "layer": "TERRENO"}
        return {"reply": "Dibujo linea inferida.", "actions": [action]}

    if any_word(text, "poligono", "polígono", "terreno", "lote", "predio", "parcela", "rectangulo", "cuadrado"):
        if "irregular" not in text and any_word(text, "regular", "lados", "hexagono", "octagono", "triangulo"):
            sides = infer_sides(text, nums)
            radius = value_after(text, "radio") or (nums[1] if len(nums) > 1 else 5)
            x, y = infer_origin(text, nums, 2)
            return {"reply": "Dibujo poligono regular inferido.", "actions": [{"type": "regular_polygon", "sides": sides, "radius": radius, "x": x, "y": y, "layer": "TERRENO"}]}
        if len(nums) >= 4 and len(nums) % 2 == 0 and not any_word(text, "origen", "desde"):
            pts = [[nums[i], nums[i + 1]] for i in range(0, len(nums), 2)]
            return {"reply": "Dibujo poligono con vertices indicados.", "actions": [{"type": "polyline", "points": pts, "closed": True, "layer": "TERRENO"}]}
        width = nums[0] if nums else 10
        height = nums[1] if len(nums) > 1 else width
        x, y = infer_origin(text, nums, 2)
        return {"reply": "Dibujo poligono rectangular inferido.", "actions": [{"type": "rectangle", "x": x, "y": y, "width": width, "height": height, "layer": "TERRENO"}]}

    return {"reply": "No estoy seguro; enviare el texto como comando directo de AutoCAD. Para mayor precision empieza con 'cad:'.", "actions": [{"type": "cad_command", "command": prompt}]}


def sanitize_plan(plan: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, dict):
        return {"reply": "El agente devolvio un plan invalido.", "actions": []}
    actions = plan.get("actions", [])
    if not isinstance(actions, list):
        actions = []
    return {"reply": str(plan.get("reply", "Plan generado.")), "actions": actions}


def normalize(value: str) -> str:
    return (
        value.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ü", "u")
        .replace("ñ", "n")
    )


def numbers(value: str) -> list[float]:
    return [float(x.replace(",", ".")) for x in re.findall(r"-?\d+(?:[\.,]\d+)?", value)]


def any_word(text: str, *words: str) -> bool:
    return any(normalize(word) in text for word in words)


def quoted(value: str) -> str:
    match = re.search(r'"([^"]+)"', value)
    return match.group(1) if match else ""


def value_after(text: str, keyword: str) -> float | None:
    match = re.search(re.escape(keyword) + r"\s*(-?\d+(?:[\.,]\d+)?)", text)
    return float(match.group(1).replace(",", ".")) if match else None


def infer_origin(text: str, nums: list[float], fallback_index: int) -> tuple[float, float]:
    match = re.search(r"(?:origen|desde|en)\s*(-?\d+(?:[\.,]\d+)?)\s*[, ]\s*(-?\d+(?:[\.,]\d+)?)", text)
    if match:
        return float(match.group(1).replace(",", ".")), float(match.group(2).replace(",", "."))
    if len(nums) >= fallback_index + 2:
        return nums[fallback_index], nums[fallback_index + 1]
    return 0, 0


def infer_sides(text: str, nums: list[float]) -> int:
    if "triangulo" in text:
        return 3
    if "hexagono" in text:
        return 6
    if "octagono" in text:
        return 8
    match = re.search(r"(\d+)\s*lados", text)
    if match:
        return int(match.group(1))
    return int(nums[0]) if nums else 6


if __name__ == "__main__":
    raise SystemExit(main())
