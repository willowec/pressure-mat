# C spi multicore

this is an example of running an spi client (slave) on one core and an spi controller (master) on the other core

[https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)

requires that the pico_sdk repository is cloned on your computer

spi tutorial: (page 152)
[https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-c-sdk.pdf](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-c-sdk.pdf)

## hardware:

Connect the two spi cahnnels absed on the following image

![image of a pico with the two spi cahnels connected](hardware.jpg)

## building:

    mkdir build
    cd build
    export PICO_SD_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
    cmake ..
    make

Then just copy the UF2 file onto the pico's flash


## build error: wrong compiler

If you compile the project and get a ton of errors about assembly instructions not being recognized, it is lieky because the wrong compiler is being used. To fix this, cd into build and remove CMakeCache.txt, then rebuild:

    cd build
    rm CMakeCache.txt
    cmake ..
    make