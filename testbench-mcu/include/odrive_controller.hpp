#ifndef __ODRIVE_CONTROLLER_H__
#define __ODRIVE_CONTROLLER_H__

#include "teensy_can.h"
#include "ODriveCAN.h"
#include "odrive_utils/odrive_msgs.hpp"
#include "odrive_utils/odrive_callbacks.hpp"

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
    /// @param odrv_user_data Reference to the ODriveUserData object
    ODriveController(FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256>& odrive_can, int CAN_ID, ODriveUserData & odrv_user_data)
        : odrive_can_(odrive_can), odrv_(ODriveCAN(wrap_can_intf(odrive_can), CAN_ID))
        {
            odrv_user_data_.node_id = CAN_ID;
            // Register callbacks for the heartbeat and encoder feedback messages
            odrv_.onFeedback(onFeedback, &odrv_user_data_);
            odrv_.onStatus(onHeartbeat, &odrv_user_data_);
            odrv_.onTemperature(onTemperature, &odrv_user_data_);
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
        odrv_.send(param);
        pumpEvents(odrive_can_);
        delay(100);
        }

        Set_Param_msg_t<uint32_t> bparam;
        for (u_int i = 0; i < bconfig_params.size(); i++) {
        bparam.Endpoint_ID = bconfig_params[i].endpoint_id;
        bparam.Value = bconfig_params[i].value;
        Serial.print("Setting param: ");
        Serial.println(bparam.Endpoint_ID);
        odrv_.send(bparam);
        pumpEvents(odrive_can_);
        delay(100);
        }

    return true;
  }

  /// @brief Run the full calibration sequence given by ODrive
  bool full_calibration()
  {
    Serial.println("Starting Calibration");
    odrv_.setState(ODriveAxisState::AXIS_STATE_FULL_CALIBRATION_SEQUENCE);
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

    odrv_.setControllerMode(
      ODriveControlMode::CONTROL_MODE_TORQUE_CONTROL,
      ODriveInputMode::INPUT_MODE_PASSTHROUGH);
    Serial.println("Setting to Torque mode");

    return true;
  }


private:

  /// @brief Address of canline for this odrive
  FlexCAN_T4<CAN, RX_SIZE_256, TX_SIZE_256> & odrive_can_;

  /// \brief Odrive object to control
  ODriveCAN odrv_;

  /// \brief struct to store user data in
  ODriveUserData & odrv_user_data_;


};

#endif // __ODRIVE_CONTROLLER_H__
