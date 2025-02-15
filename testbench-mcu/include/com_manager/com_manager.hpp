#ifndef __COM_MANAGER_H__
#define __COM_MANAGER_H__

#include "teensy_can.h"
#include <vector>
#include "com_manager/odrive_manager.hpp"
#include "com_manager/odrive_can_signals.hpp"

/// @brief Basic Communication Manager class for handling multiple CAN buses
template <CAN_DEV_TABLE CAN>
class ComManager {
public:
    /// @brief Constructor
    ComManager() = default;

    ComManager(VirtualTimerGroup &timer_group, _MB_ptr F, ICAN &teensy_can)
    : timer_group(timer_group),
      teensy_can(teensy_can){
        initializeCANBuses();
    }

    /// @brief Add a CAN bus to the manager
    void addCANBus(FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256>& canBus) {
        canBuses_.push_back(&canBus);
    }

    /// @brief Add an ODrive controller to the manager
    void addODrive(ODriveController<CAN>& odrive) {
        odrives_.push_back(&odrive);
    }

    /// @brief Initialize all CAN buses
    void initializeCANBuses() {
        for (auto* canBus : canBuses_) {
            canBus->begin();
            canBus->setBaudRate(CAN_BAUDRATE);
            canBus->setMaxMB(16);
            canBus->enableFIFO();
            canBus->enableFIFOInterrupt();
        }
    }

    /// \brief Initialize the ODrives and the Teensy CAN, must be called in setup procedure
    /// \return true if successful
    /// \return false if unsuccessful
    bool initialize() {
        find_odrives();

        for (auto* odrive : odrives_) {
            odrive.startup_odrive_checks();
        }

        startup_odrives();

        teensy_can.RegisterRXMessage(rx_end_eff_pos_message);
        teensy_can.RegisterRXMessage(rx_end_eff_vel_message);
        teensy_can.RegisterRXMessage(rx_heartbeat_message);

        return true;
    }

    /// \brief Tick Odrive CAN buses and updates timeouts
    void tick() {

        for (auto* canBus : canBuses_) {
            pumpEvents(canBus)
        }

        for (auto* odrive : odrives_) {
            odrive.odrive_user_data_.heartbeat_timeout = (millis() - odrive.odrive_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
        }

        teensy_heartbeat_timeout = (millis() - last_received_time) > TEENSY_HEARTBEAT_TIMEOUT;
        
    }

    /// \brief Communication timeout on either Teensy or ODrives
    /// \return true if any are timed out
    /// \return false if none are timed out
    void commsTimeout() {

        for (auto* odrive : odrives_) {
            if (not odrive.odrive_user_data_.heartbeat_timeout) {
                return False;
            }
        }        
        if(not teensy_heartbeat_timeout) return false;
        return true;

    }

    /// \brief Handle Teensy heartbeat message from mirroring device
    void handleHeartbeat() {
        last_received_time = millis();
    }

    /// \brief Receive hearbeats on odrives
    template <typename T>
    void find_odrives()
    {
        for (auto* odrive : odrives_) {
            Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id) + "...");
            while (not odrive.odrive_user_data_.received_heartbeat)
            {
                tick();
                delay(100);
                Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id) + "...");
            }
            Serial.println("Found ODrive");
            }
    }

    /// \brief Enable closed loop control on odrive
    void startup_odrives()
    {
        Serial.println("Enabling closed loop control...");
        while (odrive.odrive_user_data_.last_heartbeat.Axis_State != ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL)
        {
            delay(1);
            odrive.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
            for (int i = 0; i < 15; ++i)
            {
                delay(10);
                ComManager::tick();
            }
        }
        Serial.println("ODrive running!");
    }


private:
    std::vector<FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256>*> canBuses_;
    std::vector<ODriveController<CAN>*> odrives_;
    bool teensy_heartbeat_timeout = false;


    CANTXMessage<2> tx_end_eff_pos_message{teensy_can, END_EFFECTOR_POS_TX_ID, 8, 500, timer_group,
                                       end_eff_pos_0_tx, end_eff_pos_1_tx};

    CANTXMessage<2> tx_end_eff_vel_message{teensy_can, END_EFFECTOR_VEL_TX_ID, 8, 500, timer_group,
                                       end_eff_vel_0_tx, end_eff_vel_1_tx};

    CANRXMessage<2> rx_end_eff_pos_message{teensy_can, END_EFFECTOR_POS_RX_ID,
                                        end_eff_pos_0_rx, end_eff_pos_1_rx};

    CANRXMessage<2> rx_end_eff_vel_message{teensy_can, END_EFFECTOR_VEL_RX_ID,
                                        end_eff_vel_0_rx, end_eff_vel_1_rx};

    #if NUM_DRIVES == 1
    CANTXMessage<(3*1 + 2)> tx_heartbeat_message{teensy_can, HEARTBEAT_TX_ID, 1, 10000, timer_group,
        odrive0_heartbeat_active_tx, encoder0_active_tx, motor0_tx,
        mirror_system_active_tx, system_state_tx};
    #elif NUM_DRIVES == 2
    CANTXMessage<(3*2 + 2)> tx_heartbeat_message{teensy_can, HEARTBEAT_TX_ID, 1, 10000, timer_group,
        odrive0_heartbeat_active_tx, encoder0_active_tx, motor0_tx,
        odrive1_heartbeat_active_tx, encoder1_active_tx, motor1_tx,
        mirror_system_active_tx, system_state_tx};
    #elif NUM_DRIVES == 3
    CANTXMessage<(3*3 + 2)> tx_heartbeat_message{teensy_can, HEARTBEAT_TX_ID, 1, 10000, timer_group,
        odrive0_heartbeat_active_tx, encoder0_active_tx, motor0_tx,
        odrive1_heartbeat_active_tx, encoder1_active_tx, motor1_tx,
        odrive2_heartbeat_active_tx, encoder2_active_tx, motor2_tx,
        mirror_system_active_tx, system_state_tx};
    #endif

    #if NUM_DRIVES == 1
    CANRXMessage<(3*1 + 2)> rx_heartbeat_message{teensy_can, HEARTBEAT_RX_ID, [this](){handleHeartbeat();},
        odrive0_heartbeat_active_rx, encoder0_active_rx, motor0_rx,
        mirror_system_active_rx, system_state_rx};
    #elif NUM_DRIVES == 2
    CANRXMessage<(3*2 + 2)> rx_heartbeat_message{teensy_can, HEARTBEAT_RX_ID, [this](){handleHeartbeat();},
        odrive0_heartbeat_active_rx, encoder0_active_rx, motor0_rx,
        odrive1_heartbeat_active_rx, encoder1_active_rx, motor1_rx,
        mirror_system_active_rx, system_state_rx};
    #elif NUM_DRIVES == 3
    CANRXMessage<(3*3 + 2)> rx_heartbeat_message{teensy_can, HEARTBEAT_RX_ID, [this](){handleHeartbeat();},
        odrive0_heartbeat_active_rx, encoder0_active_rx, motor0_rx,
        odrive1_heartbeat_active_rx, encoder1_active_rx, motor1_rx,
        odrive2_heartbeat_active_rx, encoder2_active_rx, motor2_rx,
        mirror_system_active_rx, system_state_rx};
    #endif

    MakeUnsignedCANSignal(ControllerState, 0, 4, 1, 0) system_state_tx{};
    MakeUnsignedCANSignal(ControllerState, 0, 4, 1, 0) system_state_rx{};


};

#endif // __COM_MANAGER_H__
