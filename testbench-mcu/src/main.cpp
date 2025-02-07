// Echoing server example for the rdscom library.

#define RDSCOM_ARDUINO
#include "rdscom.hpp"
#ifdef RDSCOM_ARDUINO
#include <Arduino.h>
#endif

using namespace rdscom;

// Create a CommunicationInterfaceOptions instance with 3 retries, 2000 ms timeout, and the Arduino millis() function.
CommunicationInterfaceOptions options{3, 2000, millis};

// Instantiate a SerialCommunicationChannel using the hardware Serial port.
SerialCommunicationChannel channel{Serial};

// Create the communication interface using our serial channel.
CommunicationInterface com{channel, options};

// Define an echo prototype with identifier 1. (This must match what the sender uses.)
DataPrototype echoProto{1};

// Callback that echoes the received message.
void onEchoMessage(const Message &msg) {
    // Simply echo back the same message.
    com.sendMessage(msg);
}

void setup() {
    // Initialize the Serial port.
    Serial.begin(115200);
    while (!Serial) {
        ;  // wait for serial port to connect. (Needed for some boards.)
    }

    echoProto.addField("dummy", DataFieldType::UINT8);

    // Register the echo prototype with the communication interface.
    com.addPrototype(echoProto);

    // Register callbacks for the prototype 1 for all message types.
    com.addCallback(1, MessageType::REQUEST, onEchoMessage);
    com.addCallback(1, MessageType::RESPONSE, onEchoMessage);
    com.addCallback(1, MessageType::ERROR, onEchoMessage);

    // Optional: Print a startup message.
    Serial.println("Echo server started.");
}

void loop() {
    // Let the CommunicationInterface process any incoming messages and handle callbacks.
    com.tick();
    // You can add a short delay if desired.
    delay(10);
}
