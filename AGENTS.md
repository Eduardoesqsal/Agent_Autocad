# AGENTS.md - Contexto para el asistente de IA

## Proyecto

Servidor MCP para controlar AutoCAD mediante COM automation. El asistente puede crear, modificar y consultar dibujos de AutoCAD en tiempo real.

## Estructura del proyecto

```
autocad_mcp/
├── server.py              # Punto de entrada, registra todas las herramientas
├── core/
│   ├── autocad.py         # Conexión COM singleton con AutoCAD
│   └── layer_manager.py   # Gestión de capas
├── models/                # Dataclasses (Point, Layer, Entity)
├── drawings/              # Lógica de dibujos complejos (planos, casas, etc.)
└── tools/                 # Herramientas MCP
```

## Herramientas MCP disponibles

### Generales
- `obtener_capas` - Listar capas
- `crear_capa(nombre, color, linetype, lineweight)` - Crear capa
- `cargar_tipo_linea(nombre)` - Cargar tipo de línea
- `asignar_capa_ultima_entidad(capa, color_por_capa)` - Asignar capa a última entidad
- `asignar_props_entidad(handle, capa, color)` - Asignar propiedades por handle

### Geometría
- `crear_linea(x1, y1, x2, y2, capa, color)` - Línea
- `crear_circulo(x, y, radio, capa, color)` - Círculo
- `crear_polilinea(puntos, cerrar, capa, color)` - Polilínea
- `crear_poligono(puntos, capa, color)` - Polígono cerrado
- `insertar_texto(texto, x, y, altura, rotacion)` - Texto

### Anotación
- `anotar_distancias(altura)` - Anotar distancias de la última polilínea
- `anotar_colindantes(colindantes, capa, altura, separacion)` - Anotar colindantes alineados y desplazados hacia afuera

### Cuadros
- `cuadro_construccion(colindantes, altura_texto, escala_header, escala_area)` - Generar cuadro de coordenadas y distancias. Todos los textos del mismo tamaño por defecto (escala_header=1.0, escala_area=1.0). Columnas auto-ajustadas al contenido.
- `cuadro_curvas()` - Generar cuadro de curvas
- `reticula_utm(espaciado)` - Generar retícula UTM en cruces. SIEMPRE preguntar espaciado antes de ejecutar, no usar valor por defecto. Capa RETICULA color gris (8).

### Bloques
- `obtener_bloques()` - Listar bloques del dibujo
- `insertar_bloque(nombre, x, y, escala, rotacion, capa)` - Insertar bloque

### Información
- `info_ultima_entidad()` - Información de la última entidad
- `info_entidad(handle)` - Información por handle
- `contar_entidades()` - Contar entidades en el dibujo
- `listar_entidades()` - Listar entidades

### Edición
- `borrar_entidad(handle)` - Borrar entidad por handle
- `borrar_ultima_entidad()` - Borrar última entidad
- `mover_ultima_entidad(dx, dy)` - Mover última entidad
- `copiar_ultima_entidad(dx, dy)` - Copiar última entidad
- `rotar_ultima_entidad(angulo, cx, cy)` - Rotar última entidad
- `asignar_color_ultima_entidad(color)` - Cambiar color de última entidad

### Visualización
- `zoom_extensiones()` - Zoom Extents

### Planos predefinidos
- `generar_casa()` - Plano de casa americana 10x20m
- `generar_planta()` - Planta profesional
- `generar_alzado()` - Alzado frontal
- `generar_plano_topo()` - Plano topográfico
- `generar_propuestas()` - Propuestas arquitectónicas
- `generar_planta_bloques()` - Planta con bloques dinámicos

### Dibujo
- `obtener_dibujo_activo()` - Info del dibujo actual
- `guardar_dwg()` - Guardar dibujo

## Convenciones

- **Coordenadas**: UTM métricas (X, Y)
- **Colores AutoCAD**: 1=Rojo, 2=Amarillo, 3=Verde, 4=Cian, 5=Azul, 6=Magenta, 7=Blanco/Negro, 8=Gris, 256=PorCapa
- **Handles**: Son identificadores hexadecimales de entidades, pueden cambiar entre sesiones
- **Capas**: Crear la capa antes de asignar entidades a ella

## Flujo de trabajo típico

1. Dibujar entidades geométricas (líneas, polilíneas, polígonos)
2. Crear capas con colores específicos
3. Asignar entidades a capas (por handle o como última entidad)
4. Anotar distancias con `anotar_distancias()`
5. Anotar colindantes alineados con `anotar_colindantes()`
6. Generar cuadros con `cuadro_construccion()`
7. Insertar texto con `insertar_texto()`
8. Generar retícula UTM con `reticula_utm(espaciado)` (SIEMPRE preguntar espaciado)
9. Refrescar vista con `zoom_extensiones()`

## Notas importantes

- Los handles de entidades NO son persistentes entre sesiones del MCP
- Los textos se insertan sin capa asignada por defecto; usar `asignar_props_entidad()` después
- La herramienta `anotar_distancias()` funciona sobre todas las líneas y polilíneas del dibujo
- `anotar_colindantes()` requiere que el número de nombres coincida con los lados del polígono
- `area` se calcula manualmente con fórmula de Shoelace
- Los ángulos interiores se computan con: `θ = arccos(-(a·b) / (|a|·|b|))`

## Cambios realizados

### cuadro_construccion
- Default `altura_texto=0.6` (antes 2.0)
- Nuevos parámetros: `escala_header=1.0`, `escala_area=1.0` (todos los textos del mismo tamaño)
- Columnas auto-ajustadas al contenido: `ancho = max_chars * 0.8 * altura_texto + 2 * 0.6 * altura_texto`
- Anchos de columna base: VERTICE (4h), X (8h), Y (8h), DISTANCIA (7h), COLINDANTE (11h)
- Fila de área y perímetro sin divisiones de columna (texto libre)
- Altura de fila: 3.0 * altura_texto
- Header: 3.5 * altura_texto
- Padding: 0.6 * altura_texto
- Caracteres: ancho estimado 0.8 * altura_texto

### reticula_utm (nueva herramienta)
- Parámetro `espaciado` REQUERIDO (sin default, obliga a preguntar al usuario)
- Genera cruces (+) en lugar de líneas continuas
- Etiquetas de coordenadas en bordes
- Capa: RETICULA, color gris (8)
- Tamaño de cruz: max(1.0, spacing * 0.1)
- Altura de texto etiquetas: max(0.3, min(1.0, spacing * 0.05))

### Flujo obligatorio para retícula
1. Usuario pide "genera reticula utm"
2. PREGUNTAR siempre: "¿a qué distancia van las cruces?"
3. Esperar respuesta del usuario
4. Generar con el espaciado indicado

### Capas del proyecto
| Capa | Color | Propósito |
|------|-------|-----------|
| TERRENO | 3 (Verde) | Polígono del terreno |
| CUADRO_DATOS | 2 (Amarillo) | Cuadro de construcción |
| ANOTACIONES | 2 (Amarillo) | Distancias de lados |
| COLINDANTES | 7 (Blanco) | Nombres de colindantes |
| VERTICES | 1 (Rojo) | Etiquetas de vértices V1-Vn |
| RETICULA | 8 (Gris) | Cruces de retícula UTM |
| NOTAS | 6 (Magenta) | Notas y leyendas |

### Flujo completo recomendado (todo en uno)
1. Asegurarse de que existe un polígono cerrado en el dibujo
2. Opcional: preguntar nombres de colindantes (si no, usar nombres genéricos de ejemplo)
3. Ejecutar ordenadamente:
   - Retícula UTM (preguntar espaciado primero)
   - Cuadro de construcción con colindantes
   - Anotar distancias de cada lado
   - Anotar colindantes desplazados hacia afuera
   - Etiquetar vértices V1, V2, ... en sentido horario
4. Zoom Extents al final

### Valores por defecto actuales
- `altura_texto = 0.6` (todos los textos del mismo tamaño)
- `escala_header = 1.0`, `escala_area = 1.0`
- Columnas auto-ajustadas: ancho = max_chars × 0.8 × h + 2 × 0.6 × h
- Offset colindantes: 8m hacia afuera
- Retícula: cruces (+), etiquetas en bordes
- Conversión: 1 pulgada = 0.0254 metros

### github
echo "# Agent_Autocad" >> README.md
git init
git add .
git commit -m "Initial commit: AutoCAD MCP server"
git branch -M main
git remote add origin https://github.com/Eduardoesqsal/Agent_Autocad.git
git push -u origin main

## CI/CD Pipeline

El proyecto utiliza GitHub Actions para CI/CD definido en `.github/workflows/ci-cd.yml`.

### Pipeline configuración

| Job | Trigger | Descripción |
|-----|---------|-------------|
| `lint-and-test` | push/PR a `main` | Lint con ruff, type check con mypy, tests con pytest |
| `build-artifact` | push a `main` | Empaqueta el proyecto con `python -m build` |
| `deploy` | push a `main` | Despliegue (puede extenderse) |

### Pasos del pipeline

1. **Checkout** - Obtiene el código del repo
2. **Setup Python 3.11** - Configura el entorno
3. **Cache pip** - Caché de dependencias para velocidad
4. **Install dependencies** - `pip install -r requirements.txt` + herramientas
5. **Lint** - `ruff check` y `ruff format --check`
6. **Type check** - `mypy autocad_mcp/`
7. **Tests** - `pytest tests/`
8. **Build** - `python -m build` genera distribución
9. **Artifact** - Sube el paquete `dist/`

### Comandos locales

```bash
pip install -r requirements.txt
pip install ruff pytest mypy
ruff check autocad_mcp/
ruff format autocad_mcp/
mypy autocad_mcp/ --ignore-missing-imports
pytest tests/ -v
```

## errores 

Tu pipeline de CI/CD falló porque el código tiene múltiples violaciones de calidad detectadas por Ruff (linter) y Black (formateador). El problema principal es que en varios lugares captura excepciones genéricas con except Exception: sin especificar qué tipo de error esperas, lo que oculta bugs y hace el código difícil de depurar. Además, usas el anti-patrón try-except-pass donde ignoras silenciosamente los errores sin registrarlos, violando estándares de buenas prácticas. En autocad_mcp/core/autocad.py (líneas 543, 556, 565, 573, 581, 597) y autocad_mcp/drawings/block_plan.py (líneas 48, 50) debes reemplazar except Exception: con excepciones específicas como except (AttributeError, TypeError): y agregar logging en lugar de pass. Ejecuta black autocad_mcp/ para formatear automáticamente los 24 archivos que necesitan corrección. Una vez hagas estos cambios, el pipeline pasará sin problemas.