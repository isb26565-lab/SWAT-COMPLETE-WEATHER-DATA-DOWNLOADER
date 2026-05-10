$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here "..")

Set-Location $root

# Prefer the Python you run the app with. If you use Anaconda, run this script
# inside that environment's PowerShell prompt.
$python = "python"

Write-Host "Building SWAT Weather App EXE..." -ForegroundColor Cyan
Write-Host "Project: $root"

& $python -c "import sys; print(sys.executable); print(sys.version)"

# Ensure PyInstaller is available
$has = & $python -c "import importlib.util as u; import sys; sys.exit(0 if u.find_spec('PyInstaller') else 1)"
if ($LASTEXITCODE -ne 0) {
  Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
  & $python -m pip install --upgrade pip
  & $python -m pip install pyinstaller
}

# Clean old builds
if (Test-Path ".\\build") { Remove-Item -Recurse -Force ".\\build" }
if (Test-Path ".\\dist\\SWAT_Weather_App") { Remove-Item -Recurse -Force ".\\dist\\SWAT_Weather_App" }

# Build (onedir is more reliable for GIS libs than onefile)
& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --name "SWAT_Weather_App" `
  --windowed `
  ".\\swat_weather_app.py"

Write-Host "Done." -ForegroundColor Green
Write-Host "Output folder: dist\\SWAT_Weather_App"
