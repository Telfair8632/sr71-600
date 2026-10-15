# SR71-600 Pico firmware build script
# Usage (from anywhere):
#   powershell -ExecutionPolicy Bypass -File build.ps1 level3_minimal
#   powershell -ExecutionPolicy Bypass -File build.ps1 level4_imu
#
# NOTE: the workspace path contains non-ASCII chars (D:\...), which the ARM
# binutils cannot handle. Toolchain and build dirs therefore live under the
# pure-ASCII path D:\pico-tools; .uf2/.elf are copied back here after build.
param([Parameter(Mandatory = $true)][ValidateSet("level3_minimal", "level4_imu", "bus_doctor")][string]$Target)

$ErrorActionPreference = "Stop"
$PicoTools = "D:\pico-tools"
$Src = Join-Path $PSScriptRoot $Target
$Build = Join-Path $PicoTools "build\$Target"

$Names = @{ level3_minimal = "sr71fc_level3"; level4_imu = "sr71fc_level4"; bus_doctor = "sr71bus" }
$Name = $Names[$Target]

New-Item -ItemType Directory -Force -Path $Build | Out-Null
Copy-Item (Join-Path $Src "main.c"), (Join-Path $Src "CMakeLists.txt") $Build -Force

$env:PICO_SDK_PATH = "$PicoTools\pico-sdk"
$env:PATH = "$PicoTools\gcc-arm\bin;$PicoTools\cmake-3.31.6-windows-x86_64\bin;$PicoTools\bin;$env:PATH"

# Wait up to 8s at boot for the host to open the CDC port before printf output
# starts: without this, all output printed before the serial terminal connects
# is silently dropped (boot banner / WHO_AM_I line would never be visible).
cmake -G Ninja -B "$Build\build" -S $Build -DPICO_BOARD=pico2 -DPICO_TOOLCHAIN_PATH="$PicoTools\gcc-arm" -DPICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS=8000
if ($LASTEXITCODE -ne 0) { throw "cmake configure failed" }
cmake --build "$Build\build"
if ($LASTEXITCODE -ne 0) { throw "build failed" }

python "$PicoTools\uf2conv.py" -c -b 0x10000000 -f RP2350_ARM_S -o "$Build\$Name.uf2" "$Build\build\$Name.bin"
if ($LASTEXITCODE -ne 0) { throw "uf2 conversion failed" }

Copy-Item "$Build\$Name.uf2", "$Build\build\$Name.elf" $Src -Force
Write-Host ""
Write-Host "DONE -> $Src\$Name.uf2  (drag onto Pico 2 via BOOTSEL to flash)"