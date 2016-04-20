# Raspberry Pi Tower Light
Python script to control a 12V LED Tower light using a Raspberry Pi. This project is using custom made circuit board to switch 12V with the GPIO's without damaging them.

The basic program will use 4 GPIO outputs to send a signal to a the made board to switch 12V. More details about the board can be found below. Ofcourse if you would like to add functionality more and/or other GPIO outputs will be used.

At the moment this project only needs to monitor a single project. In the future I will implement the option to support the monitoring of multiple projects.

If you don't need to switch 12V you can still use this project to control 3V leds with the GPIO pins.

<img src="images/tower-crop.gif" alt="Adafruit LED Tower (gif)" title="Adafruit LED Tower (gif)"  width="100" />

## Installation
Install the Python [Jenkinsapi][1] package:
```sh
sudo apt-get install python-jenkinsapi
```

Clone the project in your preferred directory with:
```sh
git clone https://github.com/BramDriesen/rpi-jenkins-tower-light.git
```

Copy the default configuration file to config:
```sh
cp default-config.py config.py
```

Edit the configuration file with your Jenkins URL, Username and Password. Set the jobs to be monitored and change the GPIO outputs if needed:
```py
jenkinsurl = "http://example-url.com:8080"
username = "your-username"
password = "your-password"
jobs = ['job-name-1', 'job-name-2']
gpios = {
    'red': 18,
    'buzzer': 23,
    'yellow': 24,
    'green': 27,
}
```

Make sure to enable the setting "Wait for network on boot" in the Raspberry Pi config screen. Use `sudo raspi-config` to go to the settings.

Edit your `rc.local` file to make the script run at boot. Edit it using the command:
```sh
sudo nano /etc/rc.local
```
Using your cursor keys scroll to the bottom and add the following line :
```sh
python /path/to/the/script/rpi-jenkins-tower-light/jenkinslight.py &
```
Reboot your Raspberry Pi:
```sh
sudo reboot
```

## Light status
At startup of the scripts all light's and buzzer will be toggled once.

- Solid
    - Red: Some builds have failed
    - Yellow: Some builds are unstable
    - Green: All builds passed
- Blinking
    - Red: An error occurred (connection or authentication)
    - Yellow: One or more jobs are building

## Circuit Board
The board is created with a few simple components like 220 Ohm resistors, N-Channel MOSFET's and an Adafruit Perma Proto board HAT for the Raspberry pi.

Below you will see the component layout in Fritzing. I re-created the Perma Proto HAT board so I could have an accurate as possible layout of the component. This made the transfer to the physical board a breeze! Feel free to re-use the board for other projects.

<img src="fritzing/tower-light_bb.png" alt="Fritzing" title="Fritzing"  width="450" />

The finished circuit board attached to the Raspberry Pi zero inside of the enclosure.

<img src="images/board.png" alt="End result board" title="End result board"  width="450" />

The enclosure before closing everything up with all the switches on front. The white calble to the left is the micro-USB to USB with an Ethernet to USB connector plugged in.

<img src="images/enclosure.png" alt="Enclosure" title="Enclosure"  width="450" />

Schematics and Fritzing files can be found in the `/fritzing` directory and all the images in the `/images` directory.

#### Components used
- 4x N-Channel MOSFET (IRLB8721)
- 4x 220 Ohm resistor
- 4x Bullet connectors (3mm)
- 1x Adafruit Perma Proto HAT
- 1x Adafruit 12V LED Tower light
- 1x On/Off switch
- 1x DC Barrel power jack
- 1x 12V To USB converter
- 1x DC 12V Power adapter
- 1x Project enclosure
- Velcro tape
- Heat-shrink tubing
- 22AWG Solid copper wire
- 26AWG Flexible wire

## Version information
- V0.1-RC: Pre release version (current master)
    - Convenient setup file
    - Support for multiple jobs (todo)
    - Catching Jenkins connection and authentication errors

### Features to add / Todo list
- [x] Load settings from a config file
- [x] GPIO Setup in config file so no changes have to be made in the main script
- [x] Multiple jobs support
- [ ] Web interface to configure the settings
- [ ] Database logging + dashboard history

### Extra information
The python script has been tested on a Raspberry Pi 3 and Zero using Raspbian Jessie `4.1`.

The tower light I am using can be bought from [Adafruit][2] or other resellers that handle Adafruit products like [Pimoroni][3] where I got mine. You can probably also use other types of tower lights but be careful with operating voltages since most of the tower lights are meant for industrial applications.

[1]: https://pypi.python.org/pypi/jenkinsapi
[2]: https://www.adafruit.com/products/2993
[3]: https://shop.pimoroni.com/products/tower-light-red-yellow-green-alert-light-with-buzzer-12vdc
