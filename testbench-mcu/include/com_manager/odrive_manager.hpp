#ifndef __ODRIVE_MANAGER_H__
#define __ODRIVE_MANAGER_H__

#include "teensy_can.h"
#include "ODriveCAN.h"
#include "odrive_utils/odrive_msgs.hpp"
#include "odrive_utils/odrive_callbacks.hpp"

/// @brief ODrive Controller class for managing communication with an ODrive motor controller

template <CAN_DEV_TABLE CAN>
class ODriveManager {
public:
    // Default Constructor
    ODriveManager() = default;

    // Default Destructor
    ~ODriveManager() = default;
    
    /// @brief Constructor for the ODriveManager
    /// @param odrive_can - CAN bus that the ODrive is connected to
    /// @param CAN_ID - CAN ID of the ODrive
    /// @param odrive_user_data Reference to the ODriveUserData object
    ODriveManager(FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256>& odrive_can, int CAN_ID, ODriveUserData & odrive_user_data)
        : canbus_(odrive_can), odrive_(ODriveCAN(wrap_can_intf(odrive_can), CAN_ID))
        {
            odrive_user_data_.node_id = CAN_ID;
            // Register callbacks for the heartbeat and encoder feedback messages
            odrive_.onFeedback(onFeedback, &odrive_user_data_);
            odrive_.onStatus(onHeartbeat, &odrive_user_data_);
            odrive_.onTemperature(onTemperature, &odrive_user_data_);
        }

    /// @brief Set parameters on the ODrive
    bool set_params()
    {
        Serial.println("Setting parameters: ");
        Set_Param_msg_t<float> param;
        for (u_int i = 0; i < fconfig_params.size(); i++) {
            param.Endpoint_ID = fconfig_params[i].endpoint_id;
            param.Value = fconfig_params[i].value;

            Serial.print("Setting param: ");
            Serial.println(param.Endpoint_ID);
            odrive_.send(param);
            pumpEvents(canbus_);
            delay(100);
        }

        Set_Param_msg_t<uint32_t> bparam;
        for (u_int i = 0; i < bconfig_params.size(); i++) {
            bparam.Endpoint_ID = bconfig_params[i].endpoint_id;
            bparam.Value = bconfig_params[i].value;
            Serial.print("Setting param: ");
            Serial.println(bparam.Endpoint_ID);
            odrive_.send(bparam);
            pumpEvents(canbus_);
            delay(100);
        }

    return true;
  }

  /// @brief Run the full calibration sequence given by ODrive
  bool full_calibration()
  {
    Serial.println("Starting Calibration");
    odrive_.setState(ODriveAxisState::AXIS_STATE_FULL_CALIBRATION_SEQUENCE);
    delay(1000);
    Serial.println("Calibration Done!");
    return true;
  }

  /// @brief Set parameters and set the motor to torque control
  bool startup_odrive_checks()
  {
    Serial.println("\nAttempting to set configuration and start torque mode!");

    set_params();
    Serial.println("Configuration set");

    Serial.println("Checking Temperature...");

    odrive_.setControllerMode(ODriveControlMode::CONTROL_MODE_TORQUE_CONTROL, ODriveInputMode::INPUT_MODE_PASSTHROUGH);
    Serial.println("Setting to Torque mode");

    return true;
  }


  /// @brief Function to set the torque values based on the joint limits recorded from the startup_calibration.
  /// @param torque Requested torque in N/m
  /// @note torque is reduced when entering the buffer region.
  void set_torque(float torque)
  {
    // This is the percentage of the joint limit before we begin limiting the outputted torque
    float alpha_ = 0.95;

    const auto pos = odrive_user_data_.last_feedback.Pos_Estimate;

    // The position is outside of the joint limits
    if (pos >= motor_limits_.upper || pos <= motor_limits_.lower) {
      odrive_.setTorque(0);
      return;
    }

    // Here the joint limits are with in the acceptable range. No throttling required
    if (pos <= motor_limits_.upper * alpha_ || pos >= motor_limits_.lower * alpha_) {
      odrive_.setTorque(torque);
      return;
    }

    // If we are in the upper buffer
    if (pos >= motor_limits_.upper * alpha_) {
      const auto gain = (motor_limits_.upper - pos) / motor_limits_.upper;
      odrive_.setTorque(torque * gain);
      return;
    }

    // Only other condition is if we are in the lower buffer
    const auto gain = (motor_limits_.lower - pos) / motor_limits_.lower;
    odrive_.setTorque(torque * gain);
    return;
  }


public:

  /// @brief Address of canline for this odrive
  FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256> & canbus_;

  /// \brief Odrive object to control
  ODriveCAN odrive_;

  /// \brief struct to store user data in
  ODriveUserData & odrive_user_data_;

};

#endif // __ODRIVE_MANAGER_H__
