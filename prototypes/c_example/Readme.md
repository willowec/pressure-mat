# C example

This example is taken from a pdf tutorial by the rpi foundation. Read that for in depth info:

[https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)

requires that the pico_sdk repository is cloned on your computer

## building:

    mkdir build
    cd build
    export PICO_SD_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
    cmake ..
    make

Then just copy the UF2 file onto the pico's flash