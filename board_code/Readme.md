# Board Side Code

This directory holds the embedded code responsible for interfacing with the PCB ADC's and communicating with the connected laptop

## Usage

### Build the code:
1. Enter a linux environment (WSL)
2. 
        mkdir build
        cd build
        export PICO_SD_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
        cmake ..
        make

3. Copy the uf2 file to the pico's flash to program it
