#pragma once
#include <Arduino.h>
#include "ODriveCAN.h"
#include <FlexCAN_T4.h>
#include "ODriveFlexCAN.hpp"
#include "defines.h"
#include "odrive_utils/odrive_msgs.hpp"
#include "odrive_utils/odrive_errors.hpp"

/// \brief: Called every time a feedback message arrives from the ODrive
/// \param msg - The address of the incoming message
/// \param user_data - The pointer to the user data struct
void onFeedback(Get_Encoder_Estimates_msg_t & msg, void * user_data)
{
  ODriveUserData * odrive_user_data = static_cast<ODriveUserData *>(user_data);
  odrive_user_data->last_feedback = msg;
  odrive_user_data->received_feedback = true;
}

/// \brief: Called every time a heartbeat message arrives from the ODrive
/// \param msg - The address of the incoming message
/// \param user_data - The pointer to the user data struct
void onHeartbeat(Heartbeat_msg_t & msg, void * user_data)
{
  ODriveUserData * odrive_user_data = static_cast<ODriveUserData *>(user_data);
  odrive_user_data->last_heartbeat = msg;
  odrive_user_data->received_heartbeat = true;
  odrive_user_data->last_heartbeat_time = millis();
  if (odrive_user_data->last_error != odrive_user_data->last_heartbeat.Axis_Error) {
    odrive_user_data->last_error = odrive_user_data->last_heartbeat.Axis_Error;
    odrive_print_error(odrive_user_data->last_error);
  }
}

/// \brief: Called every time a temperature message arrives from the ODrive
/// \param msg - The address of the incoming message
/// \param user_data - The pointer to the user data struct
void onTemperature(Get_Temperature_msg_t & msg, void * user_data)
{
  ODriveUserData * odrive_user_data = static_cast<ODriveUserData *>(user_data);
  odrive_user_data->last_temperature = msg;
  odrive_user_data->received_temperature = true;
}
