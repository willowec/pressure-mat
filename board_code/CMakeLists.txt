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

include_directories("src/shared" "inc/shared")

add_executable(board_v1_main
    src/board_v1/main.c
    src/shared/transmitter.c
    src/shared/adc.c
    src/board_v1/matterface.c
    inc/shared/transmitter.h
    inc/shared/adc.h
    inc/board_v1/matterface.h 
)
target_include_directories(board_v1_main PRIVATE "inc/board_v1" PRIVATE "src/board_v1")


add_executable(board_v2_main
    src/board_v2/main.c
    src/shared/transmitter.c
    src/shared/adc.c
    src/board_v2/matterface.c
    src/shared/custom_multicore.c
    inc/shared/transmitter.h
    inc/shared/adc.h
    inc/board_v2/matterface.h 
    inc/shared/custom_multicore.h
)
target_include_directories(board_v2_main PRIVATE "inc/board_v2" PRIVATE "src/board_v2")


target_link_libraries(board_v1_main pico_stdlib pico_multicore hardware_spi)

pico_enable_stdio_usb(board_v1_main 1)
pico_enable_stdio_uart(board_v1_main 0)

pico_add_extra_outputs(board_v1_main)

target_link_libraries(board_v2_main pico_stdlib pico_multicore hardware_spi)

pico_enable_stdio_usb(board_v2_main 1)
pico_enable_stdio_uart(board_v2_main 0)

pico_add_extra_outputs(board_v2_main)