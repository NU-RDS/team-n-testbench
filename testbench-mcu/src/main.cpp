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
FingerManager finger_manager{canbus0, canbus1, odrive0, odrive1, callback_odrive0, callback_odrive1};

void setup() {

    Serial.begin(115200);

    // Wait for up to 3 seconds for the serial port to be opened on the PC side
    // If no PC connects, continue anyway
    for (int i = 0; i < 30 && !Serial; ++i)
    {
        delay(100);
    }
    delay(200);

    Serial.println("Starting CAN setup");

    if (!finger_manager.initialize())
    {
        Serial.println("CAN failed to initialize: Rebooting the teensy");
        // reboot();
    }

    Serial.println("Setup complete");

}


void loop() {

    finger_manager.move_js({0.0f, -0.1});
    finger_manager.tick();
    finger_data = finger_manager.get_finger_data();

    Serial.println(("Motor 0 Speed: ") + String(finger_data.motor_vel_estimates[0]));
    Serial.println(("Motor 1 Speed: ") + String(finger_data.motor_vel_estimates[1]));

    // Serial.println("Motor 0 - " + String(finger_data.motor_pos_estimates[0]));
    // Serial.println("Motor 1 - " + String(finger_data.motor_pos_estimates[1]));

    // Serial.println("Joint 0 - " + String(finger_data.estimated_joint_angles[0]));
    // Serial.println("Joint 1 - " + String(finger_data.estimated_joint_angles[1]));

    

    delay(5);

}