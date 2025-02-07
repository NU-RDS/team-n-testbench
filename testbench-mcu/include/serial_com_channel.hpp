#ifndef __SERIAL_COM_CHANNEL_H__
#define __SERIAL_COM_CHANNEL_H__

#include "rdscom.hpp"
#include <Arduino.h>
#include <HardwareSerial.h>

// Define a class that implements the CommunicationChannel interface for the rdscom library.
class SerialCommunicationChannel : public rdscom::CommunicationChannel {
   public:
    SerialCommunicationChannel() {};

    std::vector<std::uint8_t> receive() override {
        std::vector<std::uint8_t> data;
        while (Serial.available()) {
            data.push_back(static_cast<std::uint8_t>(Serial.read()));
        }
        return data;
    }

    void send(const rdscom::Message &message) override {
        std::vector<std::uint8_t> serialized = message.serialize();
        for (std::uint8_t byte : serialized) {
            Serial.write(byte);
        }
    }
};

#endif  // __SERIAL_COM_CHANNEL_H__