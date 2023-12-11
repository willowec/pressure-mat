# Prototype to test the feasability of sending raw data over serial

Instead of encoding data into hexadecimal for transmission from pico to pc, it should be possible to send raw data over serial. This directory is a prototype which tests that theory.

The result of this test is that yes, data can be transmitted over serial much more efficiently than by encoding to hexadecimal and decoding it on the reciever.

[https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)

requires that the pico_sdk repository is cloned on your computer

## building:

    mkdir build
    cd build
    export PICO_SDK_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
    cmake ..
    make

Then just copy the UF2 file onto the pico's flash

## Running

Plug the pico into your pc, then run

    python reciever.py "COMX"

where COMX should be the com port your pico shows up on (COM1, COM2, COM3, etc)
