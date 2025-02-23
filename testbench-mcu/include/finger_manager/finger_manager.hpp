#ifndef __FINGER_MANAGER_H__
#define __FINGER_MANAGER_H__

#include "odrive_manager/odrive_manager.hpp"
#include <Arduino.h>

const unsigned long odrive_timeout = 1000; ///< 1 second timeout

/**
 * @class FingerManager
 * @brief Manages communication for multiple CAN buses controlling robotic fingers.
 */
class FingerManager {
public:
    /// @brief Default Constructor
    FingerManager() = default;

    /**
     * @brief Parameterized constructor to initialize CAN buses and ODrive managers.
     * @param canbus0 Reference to CAN bus 0.
     * @param canbus1 Reference to CAN bus 1.
     * @param odrive0 Reference to ODriveManager for CAN bus 0.
     * @param odrive1 Reference to ODriveManager for CAN bus 1.
     * @param F Callback function for CAN bus receive events.
     */
    FingerManager(
        FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0,
        FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1,
        ODriveManager<CAN2> &odrive0,
        ODriveManager<CAN3> &odrive1,
        _MB_ptr F);

    /**
     * @brief Initialize the ODrives and the CAN buses.
     * @return true if successful, false otherwise.
     */
    bool initialize();

    /// @brief Ticks ODrive CAN buses and updates timeouts.
    void tick();

    /**
     * @brief Checks for communication timeout on either ODrive.
     * @return true if any ODrive is timed out, false otherwise.
     */
    bool comms_timeout();

    /**
     * @brief Receives heartbeats from ODrives.
     * @tparam T ODrive type.
     * @param odrive The ODrive instance to check.
     * @return true if the ODrive was found, false if timeout occurred.
     */
    template <typename T>
    bool find_odrive(T &odrive);

    /**
     * @brief Enables closed-loop control on ODrive.
     * @tparam T ODrive type.
     * @param odrive The ODrive instance to start.
     * @return true if successful, false otherwise.
     */
    template <typename T>
    bool startup_odrive(T &odrive);

public:
    FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0_; ///< CAN bus for first ODrive.
    FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1_; ///< CAN bus for second ODrive.
    ODriveManager<CAN2> &odrive0_; ///< Address of first ODrive.
    ODriveManager<CAN3> &odrive1_; ///< Address of second ODrive.
};


FingerManager::FingerManager(
    FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0,
    FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1,
    ODriveManager<CAN2> &odrive0,
    ODriveManager<CAN3> &odrive1,
    _MB_ptr F)
    : canbus0_(canbus0), canbus1_(canbus1), odrive0_(odrive0), odrive1_(odrive1) {
    
    canbus0_.begin();
    canbus0_.setBaudRate(CAN_BAUDRATE);
    canbus0_.setMaxMB(16);
    canbus0_.enableFIFO();
    canbus0_.enableFIFOInterrupt();
    canbus0_.onReceive(F);

    canbus1_.begin();
    canbus1_.setBaudRate(CAN_BAUDRATE);
    canbus1_.setMaxMB(16);
    canbus1_.enableFIFO();
    canbus1_.enableFIFOInterrupt();
    canbus1_.onReceive(F);
}

bool FingerManager::initialize() {
    bool odrive0_found = find_odrive(odrive0_);
    bool odrive1_found = find_odrive(odrive1_);

    if (!odrive0_found || !odrive1_found) {
        Serial.println("ERROR: Failed to find one or both ODrives. Initialization aborted.");
        return false;
    }

    odrive0_.startup_odrive_checks();
    odrive1_.startup_odrive_checks();

    bool odrive0_started = startup_odrive(odrive0_);
    bool odrive1_started = startup_odrive(odrive1_);

    if (!odrive0_started || !odrive1_started) {
        Serial.println("ERROR: Failed to start one or both ODrives. Initialization aborted.");
        return false;
    }

    Serial.println("Initialization successful!");
    return true;
}

void FingerManager::tick() {
    pumpEvents(canbus0_);
    pumpEvents(canbus1_);

    odrive0_.odrive_user_data_.heartbeat_timeout = (millis() - odrive0_.odrive_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
    odrive1_.odrive_user_data_.heartbeat_timeout = (millis() - odrive1_.odrive_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
}

bool FingerManager::comms_timeout() {
    return odrive0_.odrive_user_data_.heartbeat_timeout || 
           odrive1_.odrive_user_data_.heartbeat_timeout;
}

template <typename T>
bool FingerManager::find_odrive(T &odrive) {
    Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id) + "...");

    unsigned long start_time = millis();
    while (!odrive.odrive_user_data_.received_heartbeat) {
        tick();
        delay(100);
        Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id) + "...");

        if (millis() - start_time > odrive_timeout) {
            Serial.println("ERROR: Timeout while waiting for ODrive" + String(odrive.odrive_user_data_.node_id) + " heartbeat.");
            return false;
        }
    }

    Serial.println("Found ODrive" + String(odrive.odrive_user_data_.node_id));
    return true;
}

template <typename T>
bool FingerManager::startup_odrive(T &odrive) {
    Serial.println("Enabling closed loop control...");
    unsigned long start_time = millis();

    while (odrive.odrive_user_data_.last_heartbeat.Axis_State != ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL) {
        delay(1);
        odrive.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
        
        for (int i = 0; i < 15; ++i) {
            delay(10);
            tick();
        }

        if (millis() - start_time > odrive_timeout) {
            Serial.println("ERROR: Timeout while enabling closed loop control for ODrive" + String(odrive.odrive_user_data_.node_id));
            return false;
        }
    }

    Serial.println("ODrive" + String(odrive.odrive_user_data_.node_id) + " running!");
    return true;
}

#endif // __FINGER_MANAGER_H__
