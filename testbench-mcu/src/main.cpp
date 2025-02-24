// Echoing server example for the rdscom library.
#include <Arduino.h>
#include <HardwareSerial.h>

// #define RDSCOM_DEBUG_ENABLED 1
#include "rdscom.hpp"
#include "serial_com_channel.hpp"
#include "message_handlers.hpp"

#include "teensy_can.h"
#include "finger_manager/finger_manager.hpp"
#include "odrive_manager/odrive_manager.hpp"

FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> canbus0;
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> canbus1;

ODriveUserData odrive0_user_data{};
ODriveUserData odrive1_user_data{};

/// @brief: Odrive manager object for the first motor
ODriveManager<CAN2> odrive0 = ODriveManager<CAN2>(canbus0, ODRIVE0_ID, odrive0_user_data);

/// @brief: Odrive manager object for the second motor
ODriveManager<CAN3> odrive1 = ODriveManager<CAN3>(canbus1, ODRIVE1_ID, odrive1_user_data);

FingerData finger_data{};

// Called for every message that arrives on the CAN bus
void callback_odrive0(const CanMsg &msg)
{
    onReceive(msg, odrive0.odrive_);
}

void callback_odrive1(const CanMsg &msg)
{
    onReceive(msg, odrive1.odrive_);
}

/// @brief Reboot the Teensy
void reboot()
{
    SCB_AIRCR = 0x05FA0004;
}


/// @brief  Finger manager object for N demo
FingerManager g_finger_manager{canbus0, canbus1, odrive0, odrive1, callback_odrive0, callback_odrive1};

// Create a CommunicationInterfaceOptions instance with 3 retries, 2000 ms timeout, and the Arduino millis() function.
rdscom::CommunicationInterfaceOptions options{3, 2000, millis};

// Instantiate a SerialCommunicationChannel using the hardware Serial port.
SerialCommunicationChannel g_channel;

// Create the communication interface using our serial channel.
rdscom::CommunicationInterface g_com{g_channel, options};

UserCommandBuffer g_commandBuffer{g_finger_manager};

msgs::MessageHandlers g_messageHandlers{g_com, g_commandBuffer, g_finger_manager};

std::uint64_t g_loop_counter = 0;

void onExecutionComplete(UserCommandBuffer::ExecutionStats stats) {
    std::cout << "Execution complete: " << stats.executed << " commands in " << stats.time << " ms" << std::endl;
    // send a message back to the GUI
    rdscom::Message response = msgs::createControlDoneMessageRequest(
        stats.success,
        stats.time,
        stats.executed
    );
    g_com.sendMessage(response, true);
}

void onCalibrationComplete() {
    std::cout << "Calibration complete" << std::endl;
    // send a message back to the GUI
    rdscom::Message response = msgs::createZeroDoneRequest(true);
    g_com.sendMessage(response, true);
}


void setup() {
    
    Serial.begin(115200);

    while (!Serial) {
        ;  // wait for serial port to connect. (Needed for some boards.)
    }

    Serial.println("Starting CAN setup");

    if (!g_finger_manager.initialize())
    {
        Serial.println("CAN failed to initialize: Rebooting the teensy");
        // reboot();
    }

    Serial.println("Setup complete");

}

void loop() {
    g_messageHandlers.registerPrototypes();
    g_messageHandlers.addHandlers();
    g_commandBuffer.onExecutionComplete(onExecutionComplete);
    g_commandBuffer.onCalibrationComplete(onCalibrationComplete);
}