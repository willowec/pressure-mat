cmake_minimum_required(VERSION 3.13)

# The 'set' is required to build on windows apparently: https://github.com/raspberrypi/pico-examples/issues/56
set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
include(pico_sdk_import.cmake)

project(custom_multicore C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

include_directories("src" "inc")

add_executable(custom_multicore_main
    test.c
    src/custom_multicore.c
    inc/custom_multicore.h
)
pico_enable_stdio_usb(custom_multicore_main 1)

pico_add_extra_outputs(custom_multicore_main)

target_link_libraries(custom_multicore_main pico_stdlib)