// Echoing server example for the rdscom library.

#include <Arduino.h>
#include <HardwareSerial.h>

#include "rdscom.hpp"
#include "serial_com_channel.hpp"

#if defined(ARDUINO_TEENSY40) || defined(ARDUINO_TEENSY41)
#define INTERNAL_LED_PIN LED_BUILTIN
#else
#define INTERNAL_LED_PIN GPIO_NUM_2
#endif

uint8_t g_internalLEDState = HIGH;

// Create a CommunicationInterfaceOptions instance with 3 retries, 2000 ms timeout, and the Arduino millis() function.
rdscom::CommunicationInterfaceOptions options{3, 2000, millis};

// Instantiate a SerialCommunicationChannel using the hardware Serial port.
SerialCommunicationChannel channel;

// Create the communication interface using our serial channel.
rdscom::CommunicationInterface com{channel, options};

// Define an echo prototype with identifier 1. (This must match what the sender uses.)
rdscom::DataPrototype echoProto{1};

// Callback that echoes the received message.
void onEchoMessage(const rdscom::Message &msg) {
    // send back a response with the same data
    // toggle back and forth
    g_internalLEDState = (g_internalLEDState == HIGH) ? LOW : HIGH;
    digitalWrite(INTERNAL_LED_PIN, g_internalLEDState);
    rdscom::DataBuffer buf = msg.data();
    rdscom::Message response = rdscom::Message::createResponse(msg, buf);
    com.sendMessage(response);
}

void setup() {
    // Initialize the Serial port.
    Serial.begin(115200);
    while (!Serial) {
        ;  // wait for serial port to connect. (Needed for some boards.)
    }

    echoProto.addField("dummy", rdscom::DataFieldType::UINT8);

    // Register the echo prototype with the communication interface.
    com.addPrototype(echoProto);

    // Register callbacks for the prototype 1 for all message types.
    com.addCallback(1, rdscom::MessageType::REQUEST, onEchoMessage);
    com.addCallback(1, rdscom::MessageType::ERROR, onEchoMessage);

    // Optional: Print a startup message.
    Serial.println("Echo server started.");

    pinMode(INTERNAL_LED_PIN, OUTPUT);
    digitalWrite(INTERNAL_LED_PIN, g_internalLEDState);
}

void loop() {
    // Let the CommunicationInterface process any incoming messages and handle callbacks.
    com.tick();
}
