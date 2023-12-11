# Custom multicore for RP2040

This is a small multicore library for the raspberry pi pico. It is heavily based on the built-in multicore library that is provided by the Raspberry Pi Foundation. This library is used by the embedded code for the pressure mat project in ```/board_code```.

Reference:

[https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)

requires that the pico_sdk repository is cloned on your computer

## building:

    mkdir build
    cd build
    export PICO_SDK_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
    cmake ..
    make

Then just copy the UF2 file onto the pico's flash