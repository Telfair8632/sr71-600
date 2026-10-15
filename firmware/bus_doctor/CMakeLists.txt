cmake_minimum_required(VERSION 3.13)

# Build the same way as firmware/build.ps1 (toolchain: see firmware/README.md)
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

set(PICO_NO_PICOTOOL 1)

project(sr71bus C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

add_executable(sr71bus main.c)
target_link_libraries(sr71bus pico_stdlib hardware_i2c)
pico_enable_stdio_usb(sr71bus 1)
pico_enable_stdio_uart(sr71bus 0)
pico_set_program_name(sr71bus "sr71bus doctor")
pico_set_program_version(sr71bus "0.1")
pico_add_extra_outputs(sr71bus)
