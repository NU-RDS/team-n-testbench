#include "teensy_can.h"
#include "com_manager/com_manager.hpp"
#include "com_manager/odrive_manager.hpp"
#include "state_manager/state_manager.hpp"
#include <vector>

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

ComManager comms_manager{canbus0,
                         canbus1,
                         odrive0,
                         odrive1,
                         onOdriveCanMessage};

StateManager state_manager{comms_manager};                         

VirtualTimerGroup timer_group_ms{};
VirtualTimerGroup timer_group_us{};

void test() {
    odrive0.set_position(0.1);
    odrive1.set_position(0.1);
}

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

    if (!comms_manager.initialize())
    {
        Serial.println("CAN failed to initialize: reset required");
    }

    // Setup deadman switch
    ledSetup();
    pinMode(DEADMAN_SWITCH, INPUT);

    // Interrupt setup
    attachInterrupt(digitalPinToInterrupt(DEADMAN_SWITCH), []() { state_manager.check_deadman(); }, CHANGE);

    state_manager.set_active_callback(test);

    state_manager.current_state = State::INIT;

    timer_group_us.AddTimer(500, []() { state_manager.execute_state(); });
    timer_group_ms.AddTimer(10, []() { state_manager.update_led(); });
    timer_group_ms.AddTimer(10, []() { state_manager.change_state(); });

    Serial.println("Timers registered.");
    Serial.println("Exiting Setup()");

}

void loop() {

    comms_manager.tick();
    timer_group_ms.Tick(millis());
    timer_group_us.Tick(millis());

    // Serial.println("In loop");


}