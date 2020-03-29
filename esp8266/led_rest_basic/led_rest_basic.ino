#include <stdio.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>


#define IPaddress 192
#define HTTP_REST_PORT 80
#define WIFI_RETRY_DELAY 500
#define MAX_WIFI_INIT_RETRY 50

// pin number connected to LED strip
#define LED_PIN    14

// number of LEDs in strip
#define LED_COUNT 60


// define maximum brightness (max is 255)- watch out for power consumption
const int max_brightness = 100;

// LED strip object
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
// Argument 3 = Pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)


/*
set LED color and brightness with:
curl -i -X PUT -d'{"r":red_value, "g":green_value, "b":blue_value}' http://IP/leds
 */


struct Led {
    byte r;
    byte g;
    byte b;
    
} led_ressource;

const char* wifi_ssid = "SSID";
const char* wifi_passwd = "PASSWD";

// potentially IP can be set here as well with IPadress addr
ESP8266WebServer http_rest_server(HTTP_REST_PORT);

void init_led_ressource()
{
    // start with white, half brightness
    led_ressource.r = 127;
    led_ressource.g = 127;
    led_ressource.b = 127;
}

int init_wifi() {
    int retries = 0;

    Serial.println("Connecting to WiFi AP..........");
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(wifi_ssid, wifi_passwd);
    // check the status of WiFi connection to be WL_CONNECTED
    while ((WiFi.status() != WL_CONNECTED) && (retries < MAX_WIFI_INIT_RETRY)) {
        retries++;
        delay(WIFI_RETRY_DELAY);
        Serial.print("#");
    }


    // TODO: send ip address to raspi
    
    return WiFi.status(); // return the WiFi connection status
}

void json_to_resource(JsonDocument& jsonBody) {
    int r, g, b, brightness;

    // get values from json
    r = jsonBody["r"];
    g = jsonBody["g"];
    b = jsonBody["b"];

    // print values for debugging
    Serial.println(r);
    Serial.println(g);
    Serial.println(b);
    
    // set values in led object
    led_ressource.r = r;
    led_ressource.g = g;
    led_ressource.b = g;

    // apply values to led strip
    strip.fill(strip.Color(r, g, b));
    strip.show();                                          //  update strip
    
}

void get_leds() {
    StaticJsonDocument<128> jsonObj;
    String serialized;

    jsonObj["r"] = led_ressource.r;
    jsonObj["g"] = led_ressource.g;
    jsonObj["b"] = led_ressource.b;
    serializeJsonPretty(jsonObj, serialized);
    
    http_rest_server.send(200, "application/json", serialized);
}

void post_put_leds() {
    String post_body = http_rest_server.arg("plain");
    Serial.println(post_body);

    StaticJsonDocument<128> jsonObj;
    DeserializationError err = deserializeJson(jsonObj, http_rest_server.arg("plain"));

    Serial.print("HTTP Method: ");
    Serial.println(http_rest_server.method());

    if (err) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(err.c_str());
      http_rest_server.send(400);
      return;
    }
    else {   
        if (http_rest_server.method() == HTTP_POST) {
            http_rest_server.send(409);
        }
        else if (http_rest_server.method() == HTTP_PUT) {
            json_to_resource(jsonObj);
            http_rest_server.sendHeader("Location", "/leds/");
            http_rest_server.send(200);
        }
        else {
            http_rest_server.send(404);
        }
    }
}

void config_rest_server_routing() {
    http_rest_server.on("/", HTTP_GET, []() {
        http_rest_server.send(200, "text/html",
            "Welcome to the ESP8266 REST Web Server");
    });
    http_rest_server.on("/leds", HTTP_GET, get_leds);
    http_rest_server.on("/leds", HTTP_POST, post_put_leds);
    http_rest_server.on("/leds", HTTP_PUT, post_put_leds);
}

void setup(void) {
    // NodeMCU needs bitrate 9600 for serial monitor
    // Serial.begin(9600);
    Serial.begin(115200);
    //Serial.begin(74880);

    strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
    strip.show();            // Turn OFF all pixels ASAP
    strip.setBrightness(max_brightness); // set maximum overall brightness
    
    init_led_ressource();
    if (init_wifi() == WL_CONNECTED) {
        Serial.print("Connected to ");
        Serial.print(wifi_ssid);
        Serial.print("--- IP: ");
        Serial.println(WiFi.localIP());
    }
    else {
        Serial.print("Error connecting to: ");
        Serial.println(wifi_ssid);
    }

    config_rest_server_routing();

    http_rest_server.begin();
    Serial.println("HTTP REST Server Started");
}

void loop(void) {
    http_rest_server.handleClient();
}
