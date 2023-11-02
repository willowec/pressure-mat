# Custom multicore for RP2040

[https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)

requires that the pico_sdk repository is cloned on your computer

## building:

    mkdir build
    cd build
    export PICO_SDK_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
    cmake ..
    make

Then just copy the UF2 file onto the pico's flash