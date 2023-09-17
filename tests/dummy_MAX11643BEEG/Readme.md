# Dummy MAX1164BEEG

An approximation of the MAX1164BEEG ADC that runs on the rpi pico. This is used to test the embedded code of the pressure mat project during development


## Usage

### Build the code:
1. 
        mkdir build
        cd build
        export PICO_SD_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
        cmake ..
        make

2. Copy the uf2 file to the pico's flash to program it


## Design

As a programmer working on the embedded systems code for the Pressure Sensing Matrix Mat project, I want a fake MAX11643BEEG ADC to use while deveoping embedded code so that I can begin development of the project while waiting for the real ADC to ship.

Minimum viable product:

A C executable that runs on an rpi pico and

1. On core 1, acts as an SPI client which simulates the ADC:
    - must read and understand the input data byte for Setup and Conversion
    - conversion register must support scan mode 00

2. On core 2, acts as SPI controller which talks to the ADC:
    - must test all supported SPI operations and transmit results over UART to pc
    
Read the datasheet of the ADC for implementation details: [https://www.analog.com/media/en/technical-documentation/data-sheets/max11638-max11643.pdf](https://www.analog.com/media/en/technical-documentation/data-sheets/max11638-max11643.pdf)