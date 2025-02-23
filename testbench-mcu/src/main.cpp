// Echoing server example for the rdscom library.

#include <Arduino.h>
#include <HardwareSerial.h>

// #define RDSCOM_DEBUG_ENABLED 1
#include "rdscom.hpp"
#include "serial_com_channel.hpp"
#include "message_handlers.hpp"

#if defined(ARDUINO_TEENSY40) || defined(ARDUINO_TEENSY41)
#define INTERNAL_LED_PIN LED_BUILTIN
#else
#define INTERNAL_LED_PIN GPIO_NUM_2
#endif

uint8_t g_internalLEDState = HIGH;

// Create a CommunicationInterfaceOptions instance with 3 retries, 2000 ms timeout, and the Arduino millis() function.
rdscom::CommunicationInterfaceOptions options{3, 2000, millis};

// Instantiate a SerialCommunicationChannel using the hardware Serial port.
SerialCommunicationChannel g_channel;

// Create the communication interface using our serial channel.
rdscom::CommunicationInterface g_com{g_channel, options};

UserCommandBuffer g_commandBuffer;

msgs::MessageHandlers g_messageHandlers{g_com, g_commandBuffer};


void setup() {
    // Initialize the Serial port.
    Serial.begin(115200);
    while (!Serial) {
        ;  // wait for serial port to connect. (Needed for some boards.)
    }

    g_messageHandlers.registerPrototypes();
    g_messageHandlers.addHandlers();
}

void loop() {
    // Let the CommunicationInterface process any incoming messages and handle callbacks.
    g_com.tick();
}
