#ifndef __COM_MANAGER_H__
#define __COM_MANAGER_H__

#include <vector>
#include "com_manager/odrive_manager.hpp"
#include "com_manager/odrive_can_signals.hpp"

/// @brief Basic Communication Manager class for handling multiple CAN buses
class ComManager {
public:
    /// @brief Constructor
    ComManager() = default;

    ComManager(
        FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0,
        FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1,
        ODriveManager<CAN2> &odrive0,
        ODriveManager<CAN3> &odrive1,
        _MB_ptr F)
        : canbus0_(canbus0),
          canbus1_(canbus1),
          odrive0_(odrive0),
          odrive1_(odrive1)
    {
        // Initialize the CAN buses
        canbus0_.begin();
        canbus0_.setBaudRate(CAN_BAUDRATE);
        canbus0_.setMaxMB(16);
        canbus0_.enableFIFO();
        canbus0_.enableFIFOInterrupt();
        canbus0_.onReceive(F);

        // canbus1_.begin();
        // canbus1_.setBaudRate(CAN_BAUDRATE);
        // canbus1_.setMaxMB(16);
        // canbus1_.enableFIFO();
        // canbus1_.enableFIFOInterrupt();
        // canbus1_.onReceive(F);

    }


    /// \brief Initialize the ODrives and the Teensy CAN, must be called in setup procedure
    /// \return true if successful
    /// \return false if unsuccessful
    bool initialize() {
        find_odrive(odrive0_);
        // find_odrive(odrive1_);

        odrive0_.startup_odrive_checks();
        // odrive1_.startup_odrive_checks();

        startup_odrive(odrive0_);
        // startup_odrive(odrive1_);

        return true;
    }

    /// \brief Tick Odrive CAN buses and updates timeouts
    void tick() {

        pumpEvents(canbus0_);
        // pumpEvents(canbus1_);

        odrive0_.odrive_user_data_.heartbeat_timeout = (millis() - odrive0_.odrive_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
        // odrive1_.odrive_user_data_.heartbeat_timeout = (millis() - odrive1_.odrive_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
        
    }

    /// \brief Communication timeout on either of ODrives
    /// \return true if any are timed out
    /// \return false if none are timed out
    void commsTimeout() {
        return odrive0_.odrive_user_data_.heartbeat_timeout or 
            //    odrive1_.odrive_user_data_.heartbeat_timeout or

    }

    /// \brief Handle Teensy heartbeat message from mirroring device
    void handleHeartbeat() {
        last_received_time = millis();
    }

    /// \brief Receive hearbeats on odrives
    template <typename T>
    void find_odrive(T odrive)
    {
        Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id) + "...");
        while (not odrive.odrive_user_data_.received_heartbeat)
        {
            tick();
            delay(100);
            Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id) + "...");
        }
        Serial.println("Found ODrive");
    }

    /// \brief Enable closed loop control on odrive
    template <typename T>
    void startup_odrive(T odrive)
    {
        Serial.println("Enabling closed loop control...");
        while (odrive.odrive_user_data_.last_heartbeat.Axis_State != ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL)
        {
            delay(1);
            odrive.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
            
            // Pump events for 150ms. This delay is needed for two reasons;
            // 1. If there is an error condition, such as missing DC power, the ODrive might
            //    briefly attempt to enter CLOSED_LOOP_CONTROL state, so we can't rely
            //    on the first heartbeat response, so we want to receive at least two
            //    heartbeats (100ms default interval).
            // 2. If the bus is congested, the setState command won't get through
            //    immediately but can be delayed.
            for (int i = 0; i < 15; ++i)
            {
                delay(10);
                ComManager::tick();
            }
        }
        Serial.println("ODrive running!");
    }


public:

    /// \brief Canline for first odrive
    FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0_;

    /// \brief Canline for second odrive
    FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1_;

    /// \brief Address of first odrive
    OdriveController<CAN2> &odrive0_;

    /// \brief Address of second odrive
    OdriveController<CAN3> &odrive1_;    


    /// \brief: CAN Messages
    MakeUnsignedCANSignal(ControllerState, 0, 4, 1, 0) system_state_tx{};
    MakeUnsignedCANSignal(ControllerState, 0, 4, 1, 0) system_state_rx{};

    CANTXMessage<(3*2 + 2)> tx_heartbeat_message{teensy_can, HEARTBEAT_TX_ID, 1, 10000, timer_group,
                                                 odrive0_heartbeat_active_tx, encoder0_active_tx, motor0_tx,
                                                 odrive1_heartbeat_active_tx, encoder1_active_tx, motor1_tx,
                                                 mirror_system_active_tx, system_state_tx};

    CANRXMessage<(3*2 + 2)> rx_heartbeat_message{teensy_can, HEARTBEAT_RX_ID, [this](){handleHeartbeat();},
                                                 odrive0_heartbeat_active_rx, encoder0_active_rx, motor0_rx,
                                                 odrive1_heartbeat_active_rx, encoder1_active_rx, motor1_rx,
                                                 mirror_system_active_rx, system_state_rx};



};

#endif // __COM_MANAGER_H__
