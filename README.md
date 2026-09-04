# AutoCAD MCP

Servidor MCP (Model Context Protocol) para controlar AutoCAD desde asistentes de IA mediante COM automation en Python.

## Arquitectura

```
autocad_mcp/
├── server.py              # FastMCP entry point, registra todas las herramientas
├── core/
│   ├── autocad.py         # AutoCADConnection (singleton, COM automation)
│   └── layer_manager.py   # Gestión de capas
├── models/                # Dataclasses (Point, Layer, Entity)
├── drawings/              # Lógica de dibujos complejos (planos, casas, etc.)
└── tools/                 # Herramientas MCP
```

## Requisitos

- AutoCAD 2021+ (Español)
- Python 3.10+
- Windows (pywin32 / COM)

## Setup

```bash
pip install -r requirements.txt
```

## Uso

Iniciar el servidor MCP:

```bash
python -m autocad_mcp.server
```

Configurar el cliente MCP para conectarse via stdio.

## Herramientas

| Herramienta | Descripción |
|-------------|-------------|
| `obtener_capas` | Listar capas |
| `crear_capa` | Crear capa (color, linetype, lineweight) |
| `cargar_tipo_linea` | Cargar tipo de línea |
| `crear_linea` | Dibujar línea |
| `crear_circulo` | Dibujar círculo |
| `crear_polilinea` | Dibujar polilínea |
| `crear_poligono` | Dibujar polígono cerrado |
| `insertar_texto` | Insertar texto (altura, rotación) |
| `anotar_distancias` | Anotar distancias de líneas/polilíneas |
| `anotar_colindantes` | Anotar colindantes alineados a cada lado |
| `cuadro_construccion` | Cuadro de coordenadas y distancias |
| `cuadro_curvas` | Cuadro de curvas |
| `insertar_bloque` | Insertar bloque por nombre |
| `obtener_bloques` | Listar bloques del dibujo |
| `generar_casa` | Plano casa americana 10x20m |
| `generar_planta` | Planta profesional |
| `generar_planta_bloques` | Planta con bloques dinámicos |
| `generar_plano_topo` | Plano topográfico |
| `generar_alzado` | Alzado frontal |
| `generar_propuestas` | Propuestas arquitectónicas |
| `zoom_extensiones` | Zoom Extents |
| `guardar_dwg` | Guardar dibujo |
| `obtener_dibujo_activo` | Información del dibujo activo |

## Colores AutoCAD

| Código | Color |
|--------|-------|
| 1 | Rojo |
| 2 | Amarillo |
| 3 | Verde |
| 4 | Cian |
| 5 | Azul |
| 6 | Magenta |
| 7 | Blanco/Negro |
| 256 | PorCapa |

## Tipos de línea (Español)

| Español | Inglés |
|---------|--------|
| TRAZOS | DASHED |
| CENTRO | CENTER |
| TRAZO_Y_PUNTO | DASHDOT |
| DIVIDE | DIVIDE |
| PUNTO | DOT |
