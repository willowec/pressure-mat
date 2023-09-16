# Pressure Mat Project

Evan Desmond, Willow Cunningham


## Programming the RPI Pico

Getting started (on Windows):

1. Download the micropython UF2 file from the RPI website and install it on the board:

    https://www.raspberrypi.com/documentation/microcontrollers/micropython.html

2. Install Rshell

### Copying code to the RPI Pico

1. run rshell:

    On my machine, the pico connects to COM3. You can find what port the pico is connected on by looking for it under the 'Ports (COM & LPT)' dropdown in the Device Manager on Windows

        rshell --buffer-size=512 -p COM3

2. in rshell, copy the python file that you want the pico to run to /pyboard/main.py

        cp pythonfile.py /pyboard/main.py

3. disconnect the pico from power and reconnect it. Your code should then run when the pi powers on.

## Resetting the RPI Pico

If you flash the pico with some code that takes permanent control of the serial port, you will need to clear the flash of the pico to reset it. A great example of code like this is the 3x3 prototype's [board.py file](./prototypes/3x3/board.py). Lets try to avoid writing code like this for the final project.

1. Download the flash_nuke UF2 file: [https://datasheets.raspberrypi.com/soft/flash_nuke.uf2](https://datasheets.raspberrypi.com/soft/flash_nuke.uf2)
2. Connect the pico to your laptop while holding the BOOTSEL button down
3. Copy the flask_nuke.uf2 file onto the pico storage device. This will reset its flash and reboot the pico. Do not disconnect power during this process.
4. Copy the micropython UF2 file onto the pico to re-flash it.