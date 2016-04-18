# Jenkins Pi Status Light
Python script to control a 12V LED Tower light using a Raspberry Pi. This project is using custom made circuit board to switch 12V with the GPIO's without damaging them.

The basic program will use 4 GPIO outputs to send a signal to a the made board to switch 12V. More details about the board can be found below. Ofcourse if you would like to add functionality more and/or other GPIO outputs will be used.

At the moment this project only needs to monitor a single project. In the future I will implement the option to support the monitoring of multiple projects.

<img src="images/tower-crop.gif" alt="Adafruit LED Tower (gif)" title="Adafruit LED Tower (gif)"  width="200" />

## Installation
Install the Python [Jenkinsapi][1] package: `sudo apt-get install python-jenkinsapi`

Clone the project in your favourite direcotory with: `git clone https://github.com/BramDriesen/rpi-jenkins-tower-light.git`

Edit the configuration file with your Jenkins URL, Username and Password:
```py
jenkinsurl = "http://example-url.com:8080"
username = "your-username"
password = "your-password"
jobs = ['job-name-1', 'job-name-2']
```

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

Below you will find the details of the components used, the layout and electrical schema as well as the end result.


<img src="images/soon.png" alt="Fritzing" title="Fritzing"  width="250" />

<img src="images/soon.png" alt="End result board" title="End result board"  width="250" />

Schematics and Fritzing files can be found in the folder `/fritzing`.

## Version information
- V0.1-RC: Pre release version (current master)
    - Convenient setup file
    - Support for multiple jobs (todo)
    - Catching Jenkins connection and authentication errors

### Features to add / Todo list
- [x] Load settings from a config file
- [x] GPIO Setup in config file so no changes have to be made in the main script
- [ ] Upload schematics and images
- [ ] Multiple jobs support
- [ ] Web interface to configure the settings
- [ ] Code improvements
- [ ] Database logging + dashboard history

### Extra information
The python script has been tested on a Raspberry Pi 3 and Zero using Raspbian Jessie `4.1`.

The tower light I am using can be bought from [Adafruit][2] or other resellers that handle Adafruit products like [Pimoroni][3] where I got mine. You can probably also use other tpyes of tower lights but be careful with operating voltages since most of the tower lights are ment for industrial applications.

[1]: https://pypi.python.org/pypi/jenkinsapi
[2]: https://www.adafruit.com/products/2993
[3]: https://shop.pimoroni.com/products/tower-light-red-yellow-green-alert-light-with-buzzer-12vdc

