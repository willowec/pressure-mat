cmake_minimum_required(VERSION 3.13)

# initialize the SDK based on PICO_SDK_PATH
# note: this must happen before project()
set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
include(pico_sdk_import.cmake)

project(spi_example C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# initialize the Raspberry Pi Pico SDK
pico_sdk_init()

add_executable(multicore_spi
    main.c
)

target_link_libraries(multicore_spi pico_stdlib pico_multicore hardware_spi)

pico_enable_stdio_usb(multicore_spi 1)
pico_enable_stdio_uart(multicore_spi 0)


pico_add_extra_outputs(multicore_spi)