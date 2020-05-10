# smart-led
Smart Home project for controlling LED strips with a web application.

## Introduction
This project uses WS2812 LED strips and ESP8266 WiFi controller to control 
LED strips via WiFi. It also contains a web application to control multiple 
LED strips with a graphical frontend. This web application will need a device to
 run on. In my case I used a Raspberry Pi 3. 


## Set up LED Strip and WiFi Controller

### Soldering together LED Strip and ESP8266
   TODO:
   - list of parts needed
   - circuit diagram
   
### Flashing software on ESP8266
The ESP8266 can be flashed with the standard Arduino IDE. Download it and set it
up to find your ESP8266, the detailed process for that might depend on your
 operating system and there are plenty of resources describing it.

The file to be flashed on to your ESP8266 can be found here: [test](esp8266
/led_rest_api/led_rest_api.ino)
 
 
