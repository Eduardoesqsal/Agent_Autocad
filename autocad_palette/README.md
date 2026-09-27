# Codex AutoCAD Palette

Paleta lateral real tipo chat para AutoCAD 2021 hecha con .NET/C#.

## Requisitos

- AutoCAD 2021.
- Visual Studio 2019/2022 o Build Tools con .NET Framework 4.8 Developer Pack.
- VS Code puede editar el proyecto.
- El script compila con MSBuild si existe; si no, usa `csc.exe` de .NET Framework.

## Compilar

Desde PowerShell:

```powershell
.\scripts\build_palette.ps1
```

La DLL queda en:

```text
autocad_palette\bin\Release\CodexAutoCADPalette.dll
```

Si AutoCAD ya tiene cargada esa DLL, el archivo queda bloqueado. En ese caso el script genera:

```text
autocad_palette\bin\Release\CodexAutoCADPaletteChat.dll
```

## Cargar en AutoCAD en espanol

1. Ejecuta `NETLOAD`.
2. Selecciona:

```text
C:\Users\eduar\Music\Agent_Autocad\autocad_palette\bin\Release\CodexAutoCADPalette.dll
```

3. Ejecuta:

```text
CODEXPAL
```

Tambien funcionan:

```text
CODEXCHAT
CODEXPALETA
PALETACODEX
CODEXCAPAS
CODEXRETICULA
```

## Configurar OpenAI API Key

Opcion recomendada, variable de entorno de Windows:

```powershell
setx OPENAI_API_KEY "TU_API_KEY_AQUI"
```

Despues cierra y vuelve a abrir AutoCAD para que herede la variable.

Opcion local solo para este proyecto:

1. Crea este archivo:

```text
C:\Users\eduar\Music\Agent_Autocad\autocad_agent\.env.local
```

2. Adentro pon:

```text
OPENAI_API_KEY=TU_API_KEY_AQUI
OPENAI_MODEL=gpt-5
```

Ese archivo esta ignorado por git.

## Que hace

- Abre una paleta lateral acoplable gris oscuro con chat.
- Permite escribir prompts como `crea capas base`, `linea de 0,0 a 10,0`, `circulo en 5,5 radio 2`, `reticula utm cada 10`, `zoom extents` o `guardar`.
- Ejecuta acciones directamente en el dibujo activo usando la API .NET de AutoCAD.

## Prompts soportados ahora

```text
ayuda
crea un plano arquitectonico de acuerdo a normas
genera una planta arquitectonica normativa
dibuja un poligono
quiero un terreno
haz un lote de 12 x 25
poligono de 10 x 20 origen 100,200
poligono regular 6 lados radio 5 origen 0,0
crea capas base
dibuja una linea de 0,0 a 10,0
crea circulo en 5,5 radio 2
rectangulo 0,0 10,6
rectangulo 10,6
poligono 0,0 10,0 10,8 0,8
polilinea abierta 0,0 5,0 5,3
texto "NORTE" en 5,8 altura 0.5
cota de 0,0 a 10,0
anotar distancias
etiquetar vertices
mover ultima 2,0
copiar ultima 5,0
rotar ultima 45
borrar ultima
reticula utm cada 10
zoom extents
guardar dibujo
cad: _.LINE 0,0 10,0
```

Para reemplazar la DLL principal despues, cierra AutoCAD y vuelve a ejecutar:

```powershell
.\scripts\build_palette.ps1
```

Si quedan DLL antiguas en `bin\Release`, es porque AutoCAD las tiene cargadas. Cierra AutoCAD y podras borrarlas.
