# Dummy MAX1164BEEG

An approximation of the MAX1164BEEG ADC that runs on the rpi pico. This was used to test the embedded code of the pressure mat project during its early development.


## Usage

This program can run in two modes:
1. client/client mode, where both SPI0 and SPI1 host an instance of the fake ADC
2. controller/client mode, where the SPI0 channel simulates the ADC and the SPI1 channel communicates with it. Used primarily for ensuring that the ADC is being approximated correctly.

### Build the code:
1. 
        mkdir build
        cd build
        export PICO_SD_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
        cmake ..
        make

2. Copy the uf2 file to the pico's flash to program it

### Connect the pins

#### client/client mode (2 ADCs)
1. tie GP28 high to select client/client mode
2. ADC0 is available on SPI0:
    - GP2 is SCK
    - GP3 is TX
    - GP4 is RX
    - GP5 is CS
3. ADC1 is available on SPI1:
    - GP10 is SCK
    - GP11 is TX
    - GP12 is RX
    - GP13 is CS

#### controller/client mode (1 ADC)
1. tie GP28 low to select controller/client mode
2. to connect the controller to the client:
    1. connect GP2 to GP10
    2. connect GP3 to GP12
    3. connect GP4 to GP11
    4. connect GP5 to GP13


## Design

As a programmer working on the embedded systems code for the Pressure Sensing Matrix Mat project, I want a fake MAX11643BEEG ADC to use while deveoping embedded code so that I can begin development of the project while waiting for the real ADC chips to arrive.

Minimum viable product:

A C executable that runs on an rpi pico and

1. On core 1, acts as an SPI client which simulates the ADC:
    - must read and understand the input data byte for Setup and Conversion
    - conversion register must support scan mode 00

2. On core 2, acts as SPI controller which talks to the ADC:
    - must test all supported SPI operations and transmit results over UART to pc
    
Read the datasheet of the ADC for implementation details: [https://www.analog.com/media/en/technical-documentation/data-sheets/max11638-max11643.pdf](https://www.analog.com/media/en/technical-documentation/data-sheets/max11638-max11643.pdf)