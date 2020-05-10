# smart-led
Smart Home project for controlling LED strips with a web application.
This is mainly meant to be taken as an inspiration for others who want to
 implement a similar project.
 
## Introduction
This project uses WS2812 LED strips and ESP8266 WiFi controller to control 
LED strips via WiFi. It also contains a web application to control multiple 
LED strips with a graphical frontend. This web application will need a device to
 run on. In my case I used a Raspberry Pi 3. 

![frontend application](screenshot-frontend.png)

Screenshot of the frontend application to set the LED strip state.

## Web App: Development set up
### Backend set up
The backend handles http PUT requests from the frontend application to set
the state of a certain LED strip with a RGB color and an on/off variable.
The current states for all LED strips are stored in a sqlite3 database, so
that the access is thread-safe. If you want the backend to forget all devices
 which have registered, simply delete `devices.db`. The backend will create
 a new database automatically if there is no file named `devices.db`.

The backend is tested for python 3.6 and 3.8 and requires the packages in
`backend/requirements.txt` to be installed. This can for example be done using
pip:
```
pip install -r backend/requirements.txt
```
After installing all requirements you can start the backend application:
```
cd backend
python backend.py
```
Your backend should now be ready.
You can test this by registering a test LED strip manually with:
```
curl -i -H "Content-Type: application/json" -X POST --data '{"name":"test_device", "ip":"0.1.2.3"}' http://localhost:4999/devices
```
And get a list of all registered devices with:
```
curl -i -H "Content-Type: application/json" -X GET http://localhost:4999/devices
```
This list should now contain 'test_device'.

### Frontend set up
Switch to the frontend directory and install the necessary packages with
```
npm install
```
Set the IP of the device the backend is running on (probably your own
 computer at this point) in the file [App.vue](frontend/src/App.vue).

Start the front end development server with
 ```
npm run serve
```
Now open http://localhost:8080/ in a browser. If you registered a test device
in backend set up, you should now be able to see controls for this device 
similar to the screenshot above. 
You should see PUT requests arriving in the backend console when changing
the color values.

### Usage
Once you set up your ESP8266 with LED strips, you can start controlling your
led strips:

1) Make sure your frontend app and backend app are running.

2) Switch on the power on your LED strip and ESP8266.\
It is important, that you do this **after** your backend has started, because
the LED strip needs to register itself with the backend, and it does this on
start up. \
*Note: You could also modify the code for your ESP8266 to send a registration to
the backend server in a fixed time interval. Then the order in which you start
backend server and ESP8266 does not matter anymore, you might just need to
wait until the next registration is send from your ESP8266.*

3) You should now be ready to control your LED strip with the web interface.

## Set up LED Strip and WiFi Controller

### Soldering together LED Strip and ESP8266
(This part is work in progress. In the mean time you can get inspiration on
how to realise this part for example [here](https://www.instructables.com/id/ESP8266-controlling-Neopixel-LEDs-using-Arduino-ID/)).

TODO:
   - list of parts needed
   - circuit diagram
   
### Flashing software on ESP8266
Once you finished the hardware part, the ESP8266 can be flashed with the
standard Arduino IDE. Download it and set it up to find your ESP8266, the
detailed process for that might depend on your operating system and there are
 plenty of resources describing it (i.e. [here](https://randomnerdtutorials.com/how-to-install-esp8266-board-arduino-ide/)).

The file to be flashed on to your ESP8266 can be found
[here](esp8266/led_rest_api/led_rest_api.ino).
You will need to adjust some settings in this file before flashing it, such
 as your WiFi credentials, the pin you're using on the ESP8266, and the
  number of LEDs on your strip. All these settings are at the top of the file
   and are explained there.
   
Once you've flashed the file onto the ESP8266, you can test it by sending a
 simple http PUT request to the Controller. For example to set its color to
  red, send a request with curl:
  
  ```
  curl -i -X PUT -d'{"r":255, "g":0, "b":0, "power": 1}' http://[ESP8266_IP]/leds
  ```

Also check that you entered the correct IP address and port for your backend
 server in this script, as this is important for the device to be able to
  register itself on start up.


## Web App: Production set up
### Set up backend for production
 In addition to installing the requirements as described in the development
set up, I simply made the python script a service on my  Raspberry Pi, so
that it automatically starts when the Pi boots.

*Note: A more stable way to serve the backend app might be by using a uWSGI
 application server or similar, you can easily find tutorials for that (for
  example
 [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04)).*


### Set up frontend for production
You should use a webserver such as nginx or lighttpd for serving the frontend
application instead of the development server used above, as this will
probably be more stable and performant.

To build the frontend application for production, change to the `smart-led/frontend`
 directory and run
```
npm run build
```
This will create a subdirectory `dist` in the `frontend` directory, which
 contains all the files necessary to serve the static frontend web application.

The backend communicates the current state of all LED strips live to all
connected frontend clients via websockets, so that the displayed state always
matches the actual state of the LED strip.
 
For this to work, you will have to set up a proxy path in the webserver. You
will need to proxy all traffic sent to `/ws/socket.io/` to the port of your
backend. The exact way to do this will depend on the webserver
you are using. In my case (using nginx and my backend port being 4999), the
nginx site configuration file looks like this:
    
```
server {
   listen 80;
   listen [::]80;

   root [root directory of your project]/smart-led/frontend/dist;

   index index.html;

   location /ws/socket.io/ {
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_http_version 1.1;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $host;
      proxy_pass http://localhost:4999;
   }
}
```
*NOTE: This is necessary because my backend and frontend do not listen to the
same port. It is possible to handle this differently by letting the
flask backend app serve the frontend application, but this could
theoretically lead to a performance issue, as it is not recommended to serve
static directories with flask in production.* 
    


