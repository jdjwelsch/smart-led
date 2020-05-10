#include <stdio.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <ESP8266HTTPClient.h>

/*
 * This is an implementation for controlling a NeoPixel LED strip with a
 * ESP8266 WiFi Controller by http requests. It consists of two parts:
 * The first (bigger) part is the http server, receiving http PUT requests to
 * set the color of the LED strip.
 * The second part, which is currently only used on start up, is a http
 * client which sends a PUT request to the backend server to register itself
 * with a name and the IP address of the controller, so that the backend
 * knows, where to send state updates to.
 *
 * There are a few variables which need to be set for your specific set up,
 * such as the number of LEDs in your strip or your WiFi credentials.
 * They can be found below, each with an explanation.
 *
 * To test the http server side, just send a http PUT request containing r,
 * g, b, and power values to the IP address of this WiFi Controller, for
 * example with curl:
 * curl -i -X PUT -d'{"r":red_val, "g":green_val, "b":blue_val, "power": 1}'
 * http://IP/leds
 *
 * This API was inspired by https://github.com/mancusoa74/Simple_REST_ESP8266.
 */

#define IPaddress 192
#define HTTP_REST_PORT 80
#define WIFI_RETRY_DELAY 500
#define MAX_WIFI_INIT_RETRY 50

// pin number connected to LED strip
#define LED_PIN    14

// number of LEDs in strip
#define LED_COUNT 60

/*
* define maximum brightness (max is 255)- watch out for power consumption and
* take your own measurements!
* (with my setup (60 LEDs) max_brightness = 110 is equivalent to a maximum
* current of 1 A. @max_brightness = 255: max current ca 1.75 A)
*/
const int max_brightness = 110;

const char *wifi_ssid = "SSID";
const char *wifi_passwd = "PWD";
// the name this LED strip will be displayed with in the UI:
const char *device_name = "LED living room";
// endpoint and address for backend - this is where registration is send to
const char *backend_endpoint = "http://192.168.0.9:4999/devices";

// LED strip object
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// LED state object
struct Led {
    byte r;
    byte g;
    byte b;
    bool power;

} led_ressource;

// http server for sending ip and name to led control backend
ESP8266WebServer http_rest_server(HTTP_REST_PORT);

/**
 * Set up on start up.
 *
 * The LED strip is initialised with a maximum allowed brightness as set
 * above, the controller logs into WiFi and registers itself in the backend,
 * so that state_changes for this LED strip can be send back.
 */
void setup(void) {
    // set bitrate for ESP8266 serial output for debugging
    // (experiment with different values if you get weird serial output)
    Serial.begin(115200);

    strip.begin();           // initialise NeoPixel strip object
    strip.show();            // turn off all pixels
    strip.setBrightness(max_brightness); // set maximum overall brightness

    init_led_ressource();
    if (init_wifi() == WL_CONNECTED) {
        Serial.print("Connected to ");
        Serial.print(wifi_ssid);
        Serial.print("--- IP: ");
        Serial.println(WiFi.localIP());

        // send own ip and device_name to control server
        HTTPClient http;
        http.begin(backend_endpoint);
        http.addHeader("Content-Type", "application/json");
        Serial.println("Send registration to server");

        StaticJsonDocument<128> registration;
        String serialized_registration;
        registration["name"] = device_name;
        registration["ip"] = WiFi.localIP().toString();
        serializeJsonPretty(registration, serialized_registration);

        int httpCode = http.POST(serialized_registration);
        Serial.println(httpCode);

        http.end();

    } else {
        Serial.print("Error connecting to: ");
        Serial.println(wifi_ssid);
    }

    config_rest_server_routing();

    http_rest_server.begin();
    Serial.println("HTTP REST Server Started");
}

/**
 * Loop to keep listening for http requests.
 */
void loop(void) {
    http_rest_server.handleClient();
}

/**
 * Initialise LED state in off and color black.
 */
void init_led_ressource() {
    // start with white, half brightness
    led_ressource.r = 0;
    led_ressource.g = 0;
    led_ressource.b = 0;
    led_ressource.power = false;
}

/**
 * Log into wifi.
 * @return Arduino WiFi status
 */
int init_wifi() {
    int retries = 0;

    Serial.println("Connecting to WiFi AP...");

    WiFi.mode(WIFI_STA);
    WiFi.begin(wifi_ssid, wifi_passwd);
    // check the status of WiFi connection to be WL_CONNECTED and retry to
    // connect otherwise
    while ((WiFi.status() != WL_CONNECTED) && (retries < MAX_WIFI_INIT_RETRY)) {
        retries++;
        delay(WIFI_RETRY_DELAY);
        Serial.print("#");
    }

    return WiFi.status();
}

/**
 * Define routing for API endpoints.
 */
void config_rest_server_routing() {
    http_rest_server.on("/", HTTP_GET, []() {
        http_rest_server.send(200, "text/html",
                              "Welcome to the LED strip REST Web Server");
    });
    http_rest_server.on("/leds", HTTP_GET, get_leds);
    http_rest_server.on("/leds", HTTP_POST, post_put_leds);
    http_rest_server.on("/leds", HTTP_PUT, post_put_leds);
}

/**
 * Extract information from json and set state variables.
 *
 * @param jsonBody: json containing 'r', 'g', 'b', and 'power' keys for state
 * update.
 */
void change_state_from_json(JsonDocument &jsonBody) {
    int r, g, b;
    bool power;

    // get values from json
    r = jsonBody["r"];
    g = jsonBody["g"];
    b = jsonBody["b"];
    power = jsonBody["power"];

    // print values for debugging
    Serial.println(r);
    Serial.println(g);
    Serial.println(b);
    Serial.println(power);

    // apply values to led strip
    if (power) {
        // set colors (only if values have changed)
        if (r != led_ressource.r ||
            g != led_ressource.g ||
            b != led_ressource.b ||
            power != led_ressource.power) {

            smooth_transition(r, g, b);
        }
    } else {
        // set all colors to 0 if power off
        strip.fill(strip.Color(0, 0, 0));
        strip.show();
    }

    // set values in led object
    led_ressource.r = r;
    led_ressource.g = g;
    led_ressource.b = b;
    led_ressource.power = power;
}

/**
 * Do a smooth transition between current color and new color.
 *
 * @param r integer, new red value
 * @param g integer, new green value
 * @param b integer, new blue value
 */
void smooth_transition(int r, int g, int b) {
    // number of color steps used in transition
    int n_steps = 30;
    // time in seconds which the whole transition should take
    float transition_time = 1;

    // step size for single color channels
    int r_step = (int) ((r - led_ressource.r) / n_steps);
    int g_step = (int) ((g - led_ressource.g) / n_steps);
    int b_step = (int) ((b - led_ressource.b) / n_steps);

    int current_r = led_ressource.r;
    int current_g = led_ressource.g;
    int current_b = led_ressource.b;

    for (int i = 0; i < n_steps; i++) {
        current_r += r_step;
        current_g += g_step;
        current_b += b_step;

        // print current colors to serial for debugging
        Serial.println(current_r);
        Serial.println(current_g);
        Serial.println(current_b);

        // set colors in LED strip
        strip.fill(strip.Color(current_r, current_g, current_b));
        strip.show();

        // delay so that complete transition takes transition_time
        // (expects time in ms)
        delay((transition_time / n_steps) * 1000);
    }

    // ensure that color ends up at target value
    // (could be different due to rounding errors)
    strip.fill(strip.Color(r, g, b));
    strip.show();
}

/**
 * Send current state of leds to server.
 */
void get_leds() {
    StaticJsonDocument<128> jsonObj;
    String serialized;

    jsonObj["r"] = led_ressource.r;
    jsonObj["g"] = led_ressource.g;
    jsonObj["b"] = led_ressource.b;
    jsonObj["power"] = led_ressource.power;
    serializeJsonPretty(jsonObj, serialized);

    http_rest_server.send(200, "application/json", serialized);
}

/**
 * Define API endpoint for getting and setting LED state.
 */
void post_put_leds() {
    String post_body = http_rest_server.arg("plain");
    Serial.println(post_body);

    StaticJsonDocument<128> jsonObj;
    DeserializationError err = deserializeJson(jsonObj,
                                               http_rest_server.arg("plain"));

    Serial.print("HTTP Method: ");
    Serial.println(http_rest_server.method());

    if (err) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(err.c_str());
        http_rest_server.send(400);
        return;

    } else {
        if (http_rest_server.method() == HTTP_POST) {
            // send 'not allowed' as one cannot create new LED devices from
            // server
            http_rest_server.send(405);

        } else if (http_rest_server.method() == HTTP_PUT) {
            http_rest_server.sendHeader("Location", "/leds/");
            http_rest_server.send(200);
            change_state_from_json(jsonObj);

        } else {
            http_rest_server.send(404);
        }
    }
}
