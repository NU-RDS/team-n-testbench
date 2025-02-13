#ifndef __COM_MANAGER_H__
#define __COM_MANAGER_H__

#include "teensy_can.h"
#include <vector>
#include <unordered_map>
#include "odrive_controller.hpp"

#define HEARTBEAT_CHECK_INTERVAL 100  // in ms
#define HEARTBEAT_TIMEOUT 1000  // in ms

/// @brief Basic Communication Manager class for handling multiple CAN buses
template <CAN_DEV_TABLE CAN>
class ComManager {
public:
    /// @brief Constructor
    ComManager() = default;

    ComManager(VirtualTimerGroup &timer_group, _MB_ptr F, ICAN &teensy_can)
    : timer_group(timer_group), teensy_can(teensy_can) {
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
        find_odrive(odrv0_);
        find_odrive(odrv1_);

        odrv0_.startup_odrive_checks();
        odrv1_.startup_odrive_checks();

        startup_odrive(odrv0_);
        startup_odrive(odrv1_);

        teensy_can.RegisterRXMessage(rx_end_eff_pos_message);
        teensy_can.RegisterRXMessage(rx_end_eff_vel_message);
        teensy_can.RegisterRXMessage(rx_heartbeat_message);

        // Uncomment these for unmapped ODrives
        // odrv1_.enable_anticogging();
        // odrv0_.enable_anticogging();

        return true;
    }

    /// \brief Tick Odrive CAN buses and updates timeouts
    void tick() {

        for (auto* canBus : canBuses_) {
            pumpEvents(canBus)
        }
        
    }

    /// \brief Communication timeout on either Teensy or ODrives
    /// \return true if any are timed out
    /// \return false if none are timed out
    void commsTimeout() {

        for (auto* odrive : odrives_) {
            odrive.odrv_user_data_.heartbeat_timeout = (millis() - odrive.odrv_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
            if (not odrive.odrv_user_data_.heartbeat_timeout) {
                return False;
            }
        }

        teensy_heartbeat_timeout = (millis() - last_received_time) > TEENSY_HEARTBEAT_TIMEOUT;
        
        if(not teensy_heartbeat_timeout) return false;
        return true;

    }

    /// \brief Handle Teensy heartbeat message from mirroring device
    void handleHeartbeat() {
        last_received_time = millis();
    }

private:
    std::vector<FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256>*> canBuses_;
    std::vector<ODriveController<CAN>*> odrives_;
    bool teensy_heartbeat_timeout = false;
};

#endif // __COM_MANAGER_H__
