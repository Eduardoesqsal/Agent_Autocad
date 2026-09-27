$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$project = Join-Path $root "autocad_palette\CodexAutoCADPalette.csproj"

$candidates = @(
  "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
  "${env:ProgramFiles}\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
  "${env:ProgramFiles}\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe",
  "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe",
  "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe",
  "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Enterprise\MSBuild\Current\Bin\MSBuild.exe",
  "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)

$msbuild = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($msbuild) {
  & $msbuild $project /p:Configuration=Release /p:Platform=AnyCPU /m

  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
} else {
  $csc = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
  if (-not (Test-Path $csc)) {
    $csc = "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe"
  }
  if (-not (Test-Path $csc)) {
    Write-Error "No encontre MSBuild ni csc.exe de .NET Framework. Instala Visual Studio Build Tools."
  }

  $outDir = Join-Path $root "autocad_palette\bin\Release"
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null
  $outDll = Join-Path $outDir "CodexAutoCADPalette.dll"
  if (Test-Path $outDll) {
    try {
      $stream = [System.IO.File]::Open($outDll, "Open", "ReadWrite", "None")
      $stream.Close()
    } catch {
      $outDll = Join-Path $outDir "CodexAutoCADPaletteChat.dll"
      Write-Host "La DLL principal esta bloqueada por AutoCAD; generare $outDll"
      if (Test-Path $outDll) {
        try {
          $stream = [System.IO.File]::Open($outDll, "Open", "ReadWrite", "None")
          $stream.Close()
        } catch {
          $stamp = Get-Date -Format "yyyyMMddHHmmss"
          $outDll = Join-Path $outDir "CodexAutoCADPaletteChat_$stamp.dll"
          Write-Host "La DLL de chat tambien esta bloqueada; generare $outDll"
        }
      }
    }
  }
  $acad = "C:\Program Files\Autodesk\AutoCAD 2021"
  $wpf = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\WPF"
  if (-not (Test-Path $wpf)) {
    $wpf = "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\WPF"
  }

  & $csc `
    /target:library `
    /nologo `
    /out:$outDll `
    /reference:System.dll `
    /reference:System.Core.dll `
    /reference:System.Drawing.dll `
    /reference:System.Web.Extensions.dll `
    /reference:System.Windows.Forms.dll `
    /reference:"$wpf\PresentationCore.dll" `
    /reference:"$wpf\WindowsBase.dll" `
    /reference:"$acad\accoremgd.dll" `
    /reference:"$acad\acdbmgd.dll" `
    /reference:"$acad\acmgd.dll" `
    "$root\autocad_palette\Properties\AssemblyInfo.cs" `
    "$root\autocad_palette\src\CodexPalettePlugin.cs" `
    "$root\autocad_palette\src\CodexPaletteControl.cs"

  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}

Write-Host "DLL generada en $outDll"
