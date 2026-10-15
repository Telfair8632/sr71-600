cmake_minimum_required(VERSION 3.13)

# Build (set PICO_SDK_PATH and add the toolchain to PATH first; see firmware/README.md):
#   cmake -G Ninja -B build -S . -DPICO_BOARD=pico2
#   cmake --build build

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

# No MSVC host compiler on this machine: skip the SDK auto-built picotool (it
# would also disable direct .uf2 output); the UF2 is generated from the .bin
# by firmware/build.ps1 using the SDK's own tools/uf2/uf2conv.py.
set(PICO_NO_PICOTOOL 1)

project(sr71fc_level4 C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(sr71fc_level4 main.c)
target_link_libraries(sr71fc_level4
    pico_stdlib
    hardware_watchdog
    hardware_timer
    hardware_i2c
)
pico_enable_stdio_usb(sr71fc_level4 1)
pico_enable_stdio_uart(sr71fc_level4 0)
pico_set_program_name(sr71fc_level4 "sr71fc level4 mpu6050")
pico_set_program_version(sr71fc_level4 "0.1")
pico_add_extra_outputs(sr71fc_level4)
