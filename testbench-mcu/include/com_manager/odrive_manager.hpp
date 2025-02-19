#ifndef __ODRIVE_MANAGER_H__
#define __ODRIVE_MANAGER_H__

#include "teensy_can.h"
#include "ODriveCAN.h"
#include "odrive_utils/odrive_msgs.hpp"
#include "odrive_utils/odrive_callbacks.hpp"
#include "robot_description/finger.hpp"

/// @brief ODrive Controller class for managing communication with an ODrive motor controller

template <CAN_DEV_TABLE CAN>
class ODriveController {
public:
    // Default Constructor
    OdriveController() = default;

    // Default Destructor
    ~OdriveController() = default;
    
    /// @brief Constructor for the ODriveController
    /// @param odrive_can - CAN bus that the ODrive is connected to
    /// @param CAN_ID - CAN ID of the ODrive
    /// @param odrive_user_data Reference to the ODriveUserData object
    ODriveController(FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256>& odrive_can, int CAN_ID, ODriveUserData & odrive_user_data)
        : odrive_can_(odrive_can), odrive_(ODriveCAN(wrap_can_intf(odrive_can), CAN_ID))
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
        pumpEvents(odrive_can_);
        delay(100);
        }

        Set_Param_msg_t<uint32_t> bparam;
        for (u_int i = 0; i < bconfig_params.size(); i++) {
        bparam.Endpoint_ID = bconfig_params[i].endpoint_id;
        bparam.Value = bconfig_params[i].value;
        Serial.print("Setting param: ");
        Serial.println(bparam.Endpoint_ID);
        odrive_.send(bparam);
        pumpEvents(odrive_can_);
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

    odrive_.setControllerMode(
      ODriveControlMode::CONTROL_MODE_TORQUE_CONTROL,
      ODriveInputMode::INPUT_MODE_PASSTHROUGH);
    Serial.println("Setting to Torque mode");

    return true;
  }

  /// @brief Sets desired motor torque to move motor to motor angle
  /// @param phi_des Desired motor angle
  void set_position(float phi_des)
  {
    // Get motor angles
    const auto phi = odrive_user_data_.last_feedback.Pos_Estimate;
    
    // add PID
    const auto kp = 1e-1;
    const auto phi_dif = phi_des - phi;
    const auto desired_torque = kp * phi_dif;

    // Ensure torque is not too large
    if (desired_torque >= max_torque*0.8) {
      odrive_.setTorque(max_torque * 0.8);
    } else if (desired_torque <= - max_torque * 0.8) {
      odrive_.setTorque(- max_torque * 0.8);
    } else {
      odrive.setTorque(desired_torque);
    }
    return;
  }


private:

  /// @brief Address of canline for this odrive
  FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256> & odrive_can_;

  /// \brief Odrive object to control
  ODriveCAN odrive_;

  /// \brief struct to store user data in
  ODriveUserData & odrive_user_data_;


};

#endif // __ODRIVE_MANAGER_H__
