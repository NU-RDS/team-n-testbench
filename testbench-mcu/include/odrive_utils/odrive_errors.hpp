#ifndef ODRIVE_ERRORS_INCLUDE_GUARD
#define ODRIVE_ERRORS_INCLUDE_GUARD
#include "ODriveCAN.h"
#include <wiring.h>
#include <iostream>
#include <Arduino.h>

/// \brief: Clear errors deemed as "Safe to Clean Automatically"
bool clear_safe_errors(ODriveCAN odrv, uint32_t error)
{
  if (error == ODRIVE_ERROR_NONE || error == ODRIVE_ERROR_ESTOP_REQUESTED) {
    odrv.clearErrors();
    return true;
  }

  return false;
}

/// @brief Print Odrive Error Code
/// @param error - The Error Code
void odrive_print_error(uint32_t error)
{
  switch (error) {
    case ODRIVE_ERROR_NONE:
      Serial.println("ODRIVE_ERROR_NONE");
      break;

    case ODRIVE_ERROR_INITIALIZING:
      Serial.println("ODRIVE_ERROR_INITIALIZING");
      break;

    case ODRIVE_ERROR_SYSTEM_LEVEL:
      Serial.println("ODRIVE_ERROR_SYSTEM_LEVEL");
      break;

    case ODRIVE_ERROR_TIMING_ERROR:
      Serial.println("ODRIVE_ERROR_TIMING_ERROR");
      break;

    case ODRIVE_ERROR_MISSING_ESTIMATE:
      Serial.println("ODRIVE_ERROR_MISSING_ESTIMATE");
      break;

    case ODRIVE_ERROR_BAD_CONFIG:
      Serial.println("ODRIVE_ERROR_BAD_CONFIG");
      break;

    case ODRIVE_ERROR_DRV_FAULT:
      Serial.println("ODRIVE_ERROR_DRV_FAULT ");
      break;

    case ODRIVE_ERROR_MISSING_INPUT:
      Serial.println("ODRIVE_ERROR_MISSING_INPUT");
      break;

    case ODRIVE_ERROR_DC_BUS_OVER_VOLTAGE:
      Serial.println("ODRIVE_ERROR_DC_BUS_OVER_VOLTAGE");
      break;

    case ODRIVE_ERROR_DC_BUS_UNDER_VOLTAGE:
      Serial.println("ODRIVE_ERROR_DC_BUS_UNDER_VOLTAGE");
      break;

    case ODRIVE_ERROR_DC_BUS_OVER_CURRENT:
      Serial.println("ODRIVE_ERROR_DC_BUS_OVER_CURRENT");
      break;

    case ODRIVE_ERROR_DC_BUS_OVER_REGEN_CURRENT:
      Serial.println("ODRIVE_ERROR_DC_BUS_OVER_REGEN_CURRENT");
      break;

    case ODRIVE_ERROR_CURRENT_LIMIT_VIOLATION:
      Serial.println("ODRIVE_ERROR_CURRENT_LIMIT_VIOLATION");
      break;

    case ODRIVE_ERROR_MOTOR_OVER_TEMP:
      Serial.println("ODRIVE_ERROR_MOTOR_OVER_TEMP");
      break;

    case ODRIVE_ERROR_INVERTER_OVER_TEMP:
      Serial.println("ODRIVE_ERROR_INVERTER_OVER_TEMP");
      break;

    case ODRIVE_ERROR_VELOCITY_LIMIT_VIOLATION:
      Serial.println("ODRIVE_ERROR_VELOCITY_LIMIT_VIOLATION");
      break;

    case ODRIVE_ERROR_POSITION_LIMIT_VIOLATION:
      Serial.println("ODRIVE_ERROR_POSITION_LIMIT_VIOLATION");
      break;

    case ODRIVE_ERROR_WATCHDOG_TIMER_EXPIRED:
      Serial.println("ODRIVE_ERROR_WATCHDOG_TIMER_EXPIRED");
      break;

    case ODRIVE_ERROR_ESTOP_REQUESTED:
      Serial.println("ODRIVE_ERROR_ESTOP_REQUESTED");
      break;

    case ODRIVE_ERROR_SPINOUT_DETECTED:
      Serial.println("ODRIVE_ERROR_SPINOUT_DETECTED");
      break;

    case ODRIVE_ERROR_BRAKE_RESISTOR_DISARMED:
      Serial.println("ODRIVE_ERROR_BRAKE_RESISTOR_DISARMED");
      break;

    case ODRIVE_ERROR_THERMISTOR_DISCONNECTED:
      Serial.println("ODRIVE_ERROR_THERMISTOR_DISCONNECTED");
      break;

    case ODRIVE_ERROR_CALIBRATION_ERROR:
      Serial.println("ODRIVE_ERROR_CALIBRATION_ERROR");
      break;

  }

}

#endif
