#include "teensy_can.h"
#include "finger_manager/finger_manager.hpp"
#include "odrive_manager/odrive_manager.hpp"

FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> canbus0;
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> canbus1;

ODriveUserData odrive0_user_data{};
ODriveUserData odrive1_user_data{};

/// \brief: Odrive manager object for the first motor
ODriveManager<CAN2> odrive0 = ODriveManager<CAN2>(canbus0, ODRIVE0_ID, odrive0_user_data);

/// \brief: Odrive manager object for the second motor
ODriveManager<CAN3> odrive1 = ODriveManager<CAN3>(canbus1, ODRIVE1_ID, odrive1_user_data);

// Called for every message that arrives on the CAN bus
void onOdriveCanMessage(const CanMsg &msg)
{
    onReceive(msg, odrive0.odrive_);
    onReceive(msg, odrive1.odrive_);
}

FingerManager finger_mananger{canbus0,
                              canbus1,
                              odrive0,
                              odrive1,
                              onOdriveCanMessage};



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

    if (!finger_mananger.initialize())
    {
        Serial.println("CAN failed to initialize: reset required");
    }

    Serial.println("Setup complete");

}

void loop() {


    if (odrive0_user_data.received_feedback) {
        Get_Encoder_Estimates_msg_t feedback = odrive0_user_data.last_feedback;
        odrive0_user_data.received_feedback = false;
        Serial.println("odrv0-pos:");
        Serial.println(feedback.Pos_Estimate);
        Serial.println("odrv0-vel:");
        Serial.println(feedback.Vel_Estimate);

      }

}