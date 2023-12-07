# Board Side Code

This directory holds the embedded code that runs on the RPI Pico responsible for interfacing with the PCB ADC's and communicating with the connected laptop.

## Usage

The embedded code has three build targets: board_v1, board_v2, and board_v2_slow

 - board_v1.uf2: Designed to run on the v1 version of the PCB. single core, ~1Hz sample rate.
 - board_v2.uf2: Designed to run on the v2 version of the PCB. dual core, ~49Hz sample rate.
 - board_v2_slow.uf2: Designed to run on the v2 version of the PCB. dual core, rate limited to ~8Hz sample rate.

### Build the code:
1. Install the rpi pico sdk somewhere on your computer: [pico-sdk](https://github.com/raspberrypi/pico-sdk)
2. Enter a linux environment (WSL)
3. 
        mkdir build
        cd build
        export PICO_SD_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
        cmake ..
        make

4. Copy the uf2 file of the build target you want to program the pico with to the pico's flash to program it.
