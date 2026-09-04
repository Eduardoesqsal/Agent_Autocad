from __future__ import annotations

import os
import re

AUTOCAD_LANGUAGE = os.environ.get("AUTOCAD_LANG", "spanish").strip().lower()

CMD_MAP_EN_TO_ES: dict[str, str] = {
    "LINE": "LINEA",
    "CIRCLE": "CIRCULO",
    "PLINE": "POL",
    "LWPOLYLINE": "POL",
    "SPLINE": "SPLINE",
    "LAYER": "CAPA",
    "CHPROP": "CAMBIAPROP",
    "PROPERTIES": "PROPIEDADES",
    "ERASE": "BORRA",
    "COPY": "COPIA",
    "MOVE": "DESPLAZA",
    "ROTATE": "ROTA",
    "MIRROR": "SIMETRIA",
    "SCALE": "ESCALA",
    "STRETCH": "ESTIRA",
    "TRIM": "RECORTA",
    "EXTEND": "ALARGA",
    "OFFSET": "EQUISDISTANCIA",
    "ARRAY": "MATRIZ",
    "FILLET": "EMPALME",
    "CHAMFER": "CHAFLAN",
    "DIST": "DIST",
    "AREA": "AREA",
    "LIST": "LISTA",
    "DIMLINEAR": "ACOTLINEAL",
    "DIMALIGNED": "ACOTALINEADA",
    "DIMCONTINUE": "ACOTCONTINUA",
    "DIMBASELINE": "ACOTLINEABASE",
    "LEADER": "DIRECTRIZ",
    "MTEXT": "MTEXTO",
    "TEXT": "TEXTO",
    "INSERT": "INSERT",
    "BLOCK": "BLOQUE",
    "WBLOCK": "BLOQUEDIS",
    "EXPLODE": "DESCOMP",
    "PURGE": "LIMPIA",
    "ZOOM": "ZOOM",
    "PAN": "PAN",
    "REGEN": "REGEN",
    "REDRAW": "REDIBUJA",
    "GRID": "CUADRICULA",
    "SNAP": "FORZC",
    "ORTHO": "ORTO",
    "OSNAP": "REFENT",
    "UNITS": "UNIDADES",
    "LIMITS": "LIMITES",
    "LAYOUT": "PRESENTACION",
    "PLOT": "IMPRIME",
    "MATCHPROP": "COPIAPROP",
    "HATCH": "TRAMAS",
    "BHATCH": "TRAMAS",
    "GRADIENT": "DEGRADADO",
    "DIMSTYLE": "ESTILOACOT",
    "TEXTSTYLE": "ESTILOTEX",
    "LAYERSTATE": "ESTADOCAPA",
    "LAYTRANS": "TRANSCAPA",
    "LAYMRG": "UNIONCAPA",
    "LAYWALK": "RECORRECAPA",
    "LAYISO": "AISLACAPA",
    "LAYUNISO": "DESAISLACAPA",
    "LAYOFF": "APAGACAPA",
    "LAYON": "PRENDECAPA",
    "LAYFRZ": "CONGCAPA",
    "LAYTHW": "DESCONGCAPA",
    "LAYLCK": "BLOQCAPA",
    "LAYULK": "DESBLOQCAPA",
    "SELECT": "SELECC",
    "GROUP": "GRUPO",
    "UNGROUP": "DESAGRUP",
    "ALIGN": "ALINEA",
    "XREF": "REFEX",
    "ATTACH": "ADHERIR",
    "IMAGE": "IMAGEN",
    "DWFATTACH": "ADHERIRDWF",
    "PDFATTACH": "ADHERIRPDF",
    "DGNATTACH": "ADHERIRDGN",
    "UNDO": "DESHACE",
    "REDO": "REHACE",
    "SAVE": "GUARDA",
    "SAVEAS": "GUARDACOMO",
    "OPEN": "ABRE",
    "CLOSE": "CIERRA",
    "NEW": "NUEVO",
    "QUIT": "SALE",
    "EXPORT": "EXPORTA",
    "IMPORT": "IMPORTA",
    "AUDIT": "VERIFICA",
    "RECOVER": "RECUPERA",
    "DWGPROPS": "PROPIEDADESDWG",
    "APPLOAD": "CARGAAPLICACION",
    "VBALOAD": "CARGAVBA",
    "VBAUNLOAD": "DESCARGAVBA",
    "VBAIDE": "EDITORVBA",
    "VLISP": "VLISP",
    "LISP": "LISP",
    "CUI": "CUI",
    "MENU": "MENU",
    "MENULOAD": "CARGAMENU",
    "MENUUNLOAD": "DESCARGAMENU",
    "TOOLBAR": "BARRAHERRAMIENTAS",
    "TOOLBOX": "CAJAHERRAMIENTAS",
    "PREFERENCES": "PREFERENCIAS",
    "OPTIONS": "OPCIONES",
}

CMD_MAP_ES_TO_EN = {v: k for k, v in CMD_MAP_EN_TO_ES.items()}


def is_spanish() -> bool:
    return AUTOCAD_LANGUAGE == "spanish"


def translate_cmd(cmd: str, to_lang: str | None = None) -> str:
    if to_lang is None:
        to_lang = AUTOCAD_LANGUAGE

    if cmd.startswith("_.") or cmd.startswith("_") and len(cmd) > 1 and cmd[1] == ".":
        return cmd

    cmd_clean = cmd.lstrip("_")

    if to_lang == "spanish":
        cmd_up = cmd_clean.upper()
        if cmd_up in CMD_MAP_EN_TO_ES:
            translated = CMD_MAP_EN_TO_ES[cmd_up]
            if cmd_clean[0].islower() if cmd_clean else False:
                translated = translated.lower()
            return f"{translated} "
        return cmd
    else:
        cmd_up = cmd_clean.upper()
        if cmd_up in CMD_MAP_ES_TO_EN:
            translated = CMD_MAP_ES_TO_EN[cmd_up]
            if cmd_clean[0].islower() if cmd_clean else False:
                translated = translated.lower()
            return translated
        return cmd


def is_standard_autocad_cmd(cmd: str) -> bool:
    cmd_clean = cmd.lstrip("_").lstrip(".").upper()
    base = re.split(r"[ \n]", cmd_clean)[0]
    return base in CMD_MAP_EN_TO_ES or base in CMD_MAP_ES_TO_EN
