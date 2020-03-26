#include <stdio.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>

#define IPaddress 192
#define HTTP_REST_PORT 80
#define WIFI_RETRY_DELAY 500
#define MAX_WIFI_INIT_RETRY 50

struct Led {
    byte id;
    byte gpio;
    byte status;
} led_ressource;

const char* wifi_ssid = "SSID";
const char* wifi_passwd = "PASSWORD";

// potentially IP can be set here as well with IPadress addr
ESP8266WebServer http_rest_server(HTTP_REST_PORT);

void init_led_ressource()
{
    led_ressource.id = 1;
    led_ressource.gpio = 16;
    led_ressource.status = LOW;
}

int init_wifi() {
    int retries = 0;

    Serial.println("Connecting to WiFi AP..........");
    //this does not work yet:
    /*
    IPAddress ip(192,168,0,70);   
    IPAddress gateway(192,168,1,254);   
    IPAddress subnet(255,255,255,0);   
    
    WiFi.config(ip, gateway, subnet);
    */
    WiFi.mode(WIFI_STA);
    WiFi.begin(wifi_ssid, wifi_passwd);
    // check the status of WiFi connection to be WL_CONNECTED
    while ((WiFi.status() != WL_CONNECTED) && (retries < MAX_WIFI_INIT_RETRY)) {
        retries++;
        delay(WIFI_RETRY_DELAY);
        Serial.print("#");
    }
    return WiFi.status(); // return the WiFi connection status
}

void get_leds() {
    //StaticJsonBuffer<200> jsonBuffer;
    StaticJsonDocument<128> jsonObj;
    //JsonObject jsonObj = jsonBuffer.createObject();
    //char JSONmessageBuffer[200];
    String serialized;

    if (led_ressource.id == 0)
        http_rest_server.send(204);
    else {
        jsonObj["id"] = led_ressource.id;
        jsonObj["gpio"] = led_ressource.gpio;
        jsonObj["status"] = led_ressource.status;
        //jsonObj.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
        serializeJsonPretty(jsonObj, serialized);
        
        //http_rest_server.send(200, "application/json", JSONmessageBuffer);
        
        // TODO!
        
        http_rest_server.send(200, "application/json", serialized);
    }
}

// void json_to_ressource(JsonObject jsonBody) {
void json_to_ressource(JsonDocument& jsonBody) {
    int id, gpio, status;

    id = jsonBody["id"];
    gpio = jsonBody["gpio"];
    status = jsonBody["status"];

    Serial.println(id);
    Serial.println(gpio);
    Serial.println(status);

    led_ressource.id = id;
    led_ressource.gpio = gpio;
    led_ressource.status = status;
    
    pinMode(led_ressource.gpio, OUTPUT);
    // this is probably just for the built in LED:
    if (led_ressource.status == 0) {
      digitalWrite(led_ressource.gpio, HIGH);  
    }
    else {
      digitalWrite(led_ressource.gpio, LOW);
    }
    
}

void post_put_leds() {
    //StaticJsonBuffer<500> jsonBuffer;
    String post_body = http_rest_server.arg("plain");
    Serial.println(post_body);

    StaticJsonDocument<128> jsonObj;
    DeserializationError err = deserializeJson(jsonObj, http_rest_server.arg("plain"));
    // JsonObject jsonBody = jsonBuffer.parseObject(http_rest_server.arg("plain"));

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
            if ((jsonObj["id"] != 0) && (jsonObj["id"] != led_ressource.id)) {
                json_to_ressource(jsonObj);
                http_rest_server.sendHeader("Location", "/leds/" + String(led_ressource.id));
                http_rest_server.send(201);
                pinMode(led_ressource.gpio, OUTPUT);
            }
            else if (jsonObj["id"] == 0)
              http_rest_server.send(404);
            else if (jsonObj["id"] == led_ressource.id)
              http_rest_server.send(409);
        }
        else if (http_rest_server.method() == HTTP_PUT) {
            if (jsonObj["id"] == led_ressource.id) {
                json_to_ressource(jsonObj);
                http_rest_server.sendHeader("Location", "/leds/" + String(led_ressource.id));
                http_rest_server.send(200);
            }
            else
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
    //Serial.begin(115200);
    Serial.begin(9600);
    
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
