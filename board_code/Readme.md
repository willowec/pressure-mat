# Board Side Code

This directory holds the embedded code that runs on the RPi Pico responsible for interfacing with the PMI PCB's ADC's and communicating with the connected laptop.

## Usage

The embedded code has three build targets: board_v1, board_v2, and board_v2_slow

 - board_v1.uf2: Designed to run on the v1 version of the PCB. single core, ~1Hz sample rate.
 - board_v2.uf2: Designed to run on the v2 version of the PCB. dual core, ~49Hz sample rate (rate limited by the computer's ability to handle serial communications).
 - board_v2_slow.uf2: Designed to run on the v2 version of the PCB. dual core, rate limited to ~8Hz sample rate.

### Build the code:
1. Install the rpi pico sdk somewhere on your computer: [pico-sdk](https://github.com/raspberrypi/pico-sdk)
2. Enter a linux environment (WSL)
3. 
        mkdir build
        cd build
        export PICO_SDK_PATH=../relative/path/to/the/cloned/directory/named/pico-sdk
        cmake ..
        make

4. Copy the uf2 file of the build target you want to program the pico with to the pico's flash to program it.

### Communicating With The Board

After connecting the programmed RPi Pico to your computer via usb, it can be talked to over serial. The board can understand the following commands:

1. PRINT_INFO:

    message:

        print_info
        
    response:

    The board prints a short message identifying its software version and then awaits further commands.

2. GET_CAL_VALS:

    message:

        get_cal_vals
        
    response:

    The board reads the mat in full once and transmits the collected data over serial before waiting for further commands. See [Mat Data Transmission Format](#mat-data-transmission-format) for more information.


3. START_READING:

    message:

        start_reading
        
    response:

    The board stops listening to commands and begins reading and transmitting sensor values over serial. The board will continue to read and transmit mat data until unpowered. See [Mat Data Transmission Format](#mat-data-transmission-format) for more information.


### Mat Data Transmission Format

The board code is designed to interface a 28x56 array of resistive pressure sensors, where data from each sensor is recorded by an 8-bit ADC. Each time the mat is read, 1,568 8-bit values must be transmitted over serial. This transmission is performed in accordance with the following format, where bytes 1-4 are the verification sequence and bytes 5-1572 are the values that the ADCs on the PCB recorded for each sensor:

        byte number:           1       2       3       4       5       6               1571    1572
        character value:       0xFF    0xFE    0xFE    0xFF    0xXX    0xXX    ...     0xXX    0xXX