param(
  [string]$PythonExe = 'C:\Users\Telfair\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
  [string]$FreeCADPython = ''
)
# Regenerates the digital package: CAD, drawings, DXFs, PDFs, docs and the offline viewer.
# Requirements: FreeCAD 1.1.3 (bundled Python 3.11) for the CAD steps, and a Python 3.12
# with ezdxf / shapely / reportlab / pymupdf for the artifact steps (or a tools/pydeps
# folder next to this repository, which the scripts pick up automatically).
$ErrorActionPreference = 'Stop'
$ProjectRoot = $PSScriptRoot
if (-not $FreeCADPython) {
  $FreeCADPython = Join-Path $ProjectRoot 'tools\FreeCAD\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe'
}
if (-not (Test-Path -LiteralPath $PythonExe)) {
  $fallback = Get-Command python -ErrorAction SilentlyContinue
  if ($fallback) { $PythonExe = $fallback.Source } else { throw 'Python runtime not found; pass -PythonExe.' }
}
if (-not (Test-Path -LiteralPath $FreeCADPython)) { throw 'FreeCAD Python not found; pass -FreeCADPython.' }
function Run-ProjectStep([string]$Runtime, [string]$Script) {
  $TaskScript = Join-Path $ProjectRoot ('src\' + $Script)
  & $Runtime $TaskScript
  if ($LASTEXITCODE -ne 0) { throw "Failed: $Script" }
}
Run-ProjectStep $FreeCADPython 'build_cad.py'
Run-ProjectStep $PythonExe 'design.py'
Run-ProjectStep $FreeCADPython 'validate_cad.py'
Run-ProjectStep $PythonExe 'viewer.py'
Run-ProjectStep $PythonExe 'raster_preview.py'
Run-ProjectStep $PythonExe 'deliverables.py'
Run-ProjectStep $PythonExe 'assembly_packets.py'
Run-ProjectStep $PythonExe 'generate_circuit_pdf.py'
Run-ProjectStep $PythonExe 'qa_documents.py'
Run-ProjectStep $PythonExe 'package_project.py'
Write-Output 'Digital package regenerated. Physical measurements and visual review remain separate.'
