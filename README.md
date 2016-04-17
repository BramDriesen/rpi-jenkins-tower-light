# Jenkins Pi Status Light
Python script to control a 12V LED Tower light using a Raspberry Pi. This project is using custom made circuit board to switch 12V with the GPIO's without damaging them.

The basic program will use 4 GPIO outputs to send a signal to a the made board to switch 12V. More details about the board can be found below. Ofcourse if you would like to add functionallity more and/or other GPIO outputs will be used.

## Installation
Install the Python [Jenkinsapi][1] package: `sudo apt-get install python-jenkinsapi`

Clone the project in your favourite direcotory with: `git clone https://github.com/BramDriesen/rpi-jenkins-tower-light.git`

Edit the configuration file with your Jenkins URL, Username and Password (TODO)

Edit the crontab configuration so the script starts at every reboot/start-up:
```sh
sudo crontab -e
```
Using your cursor keys scroll to the bottom and add the following line :
```sh
@reboot python /path/to/the/script/rpi-jenkins-tower-light/jenkinslight.py &
```
Reboot your Raspberry Pi
```sh
sudo reboot
```

## Circuit Board
The board is created with a few simple components like 220 Ohm resistors, N-MOSFET's and an Adafruit Perma Proto board hat for the Raspberry pi.

Below you will find the details of the components used, the layout and elictrical schema as well as the end result.

[image here]

[schematic here]

[end result here]

## Version information

### Features to add
- Web interface to configure the settings
- Code improvements
- Multiple projects support

### Extra information
The python script has been tested on a Raspberry Pi 3 and Zero using Raspbian Jessie `4.1`.

[1]: https://pypi.python.org/pypi/jenkinsapi
