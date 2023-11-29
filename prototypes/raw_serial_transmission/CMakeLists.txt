cmake_minimum_required(VERSION 3.13)

# The 'set' is required to build on windows apparently: https://github.com/raspberrypi/pico-examples/issues/56
set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
include(pico_sdk_import.cmake)

project(custom_multicore C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

include_directories("src" "inc")

add_executable(raw_transmission
    test.c
    src/transmitter.c
    inc/transmitter.h
)
pico_enable_stdio_usb(raw_transmission 1)

pico_add_extra_outputs(raw_transmission)

target_link_libraries(raw_transmission pico_stdlib)