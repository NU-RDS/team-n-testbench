#ifndef __COM_MANAGER_H__
#define __COM_MANAGER_H__

#include "teensy_can.h"
#include <vector>
#include "com_manager/odrive_manager.hpp"

/// @brief Proportional gain
const auto kp = 0.005;

/// @brief Motor torque limit
const auto motor_torque_limit = 0.036; // N-m

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
            // odrive.odrv_.clearErrors();
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

    /// @brief Moves the first joint to a desired angle.
    /// @param theta_des desired angle of the first joint (rad).
    void move_j1(float theta_des) 
    {
        // Get position difference
        const auto phi_0 = odrives_.at(0).odrive_user_data_.last_feedback.Pos_Estimate;
        const auto phi_1 = odrives_.at(1).odrive_user_data_.last_feedback.Pos_Estimate; 
        const auto joint_thetas = motors_to_joints({phi_0, phi_1}); // TODO: ONCE WE CALIBRATE CHANGE FUNCTION TO PHI TO THETA
        const auto theta_0_dif = theta_des - joint_thetas.at(0);

        // Send joints and get motor torque
        const auto tau_0 = kp * theta_0_dif;
        const auto torques = tau_to_torque({tau_0, 0.0});

        // Send torque
        const auto torque_0 = limit<float>(torques.at(0), motor_torque_limit);
        const auto torque_1 = limit<float>(torques.at(1), motor_torque_limit);
        odrives_.at(0).odrv_.setTorque(torque_0);
        odrives_.at(1).odrv_.setTorque(torque_1);
    }

    /// @brief Moves the second joint to a desired angle.
    /// @param theta_des desired angle of the second joint (rad).
    void move_j2(float theta_des) 
    {
        // Get position difference
        const auto phi_0 = odrives_.at(0).odrive_user_data_.last_feedback.Pos_Estimate;
        const auto phi_1 = odrives_.at(1).odrive_user_data_.last_feedback.Pos_Estimate; 
        const auto joint_thetas = motors_to_joints({phi_0, phi_1}); // TODO: ONCE WE CALIBRATE CHANGE FUNCTION TO PHI TO THETA
        const auto theta_1_dif = theta_des - joint_thetas.at(1);

        // Send joints and get motor torque
        const auto tau_1 = kp * theta_1_dif;
        const auto torques = tau_to_torque({0.0, tau_1});

        // Send torque
        const auto torque_0 = limit<float>(torques.at(0), motor_torque_limit);
        const auto torque_1 = limit<float>(torques.at(1), motor_torque_limit);
        odrives_.at(0).odrv_.setTorque(torque_0);
        odrives_.at(1).odrv_.setTorque(torque_1);
    }

private:
    std::vector<FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256>*> canBuses_;
    std::vector<ODriveController<CAN>*> odrives_;
    bool teensy_heartbeat_timeout = false;
};

#endif // __COM_MANAGER_H__
