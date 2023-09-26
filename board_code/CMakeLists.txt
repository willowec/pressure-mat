cmake_minimum_required(VERSION 3.13)

# initialize the SDK based on PICO_SDK_PATH
# note: this must happen before project()
set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
include(pico_sdk_import.cmake)

project(board_code C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# initialize the Raspberry Pi Pico SDK
pico_sdk_init()

include_directories("src" "inc")

add_executable(board_code_main
    src/main.c
    src/transmitter.c
    src/adc.c
    inc/transmitter.h
    inc/adc.h
    
)


target_link_libraries(board_code_main pico_stdlib pico_multicore hardware_spi)

pico_enable_stdio_usb(board_code_main 1)
pico_enable_stdio_uart(board_code_main 0)


pico_add_extra_outputs(board_code_main)