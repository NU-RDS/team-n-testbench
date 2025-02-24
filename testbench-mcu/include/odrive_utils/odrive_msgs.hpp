#ifndef ODRIVEMSGSHPP
#define ODRIVEMSGSHPP
#include <stdint.h>
#include "can_helpers.hpp"
#include <string>
#include "utils/filters.hpp"

/// \brief: The Struct to contain feedback from the ODrive
struct ODriveUserData
{
  Heartbeat_msg_t last_heartbeat;
  bool received_heartbeat = false;
  Get_Encoder_Estimates_msg_t last_feedback;
  bool received_feedback = false;
  uint32_t node_id;
  uint32_t last_heartbeat_time;
  bool heartbeat_timeout = false;
  uint32_t last_error;
  Get_Temperature_msg_t last_temperature;
  bool received_temperature = false;
  MovingAverageFilter pos_filter = MovingAverageFilter(5); /// Moving average filter for position estimates
  MovingAverageFilter vel_filter = MovingAverageFilter(5); /// Moving average filter for velocity estimates
  MovingAverageFilter motor_temp_filter = MovingAverageFilter(5); /// Moving average filter for motor temp estimates
  MovingAverageFilter fet_temp_filter = MovingAverageFilter(5); /// Moving average filter for FET temp estimates
};

/// \brief Structure for setting ODrive Parameters
/// Endpoint_ids can be found at the following link: https://odrive-cdn.nyc3.digitaloceanspaces.com/releases/firmware/laZ44T35qb_uR6AW6S5RdTrOL9sqZlc2_FonY3vm21Q/flat_endpoints.json
template<typename T>
struct Set_Param_msg_t final
{
  constexpr Set_Param_msg_t() = default;

#ifdef ODRIVE_CAN_MSG_TYPE
  Set_Param_msg_t(const TBoard::TCanIntf::TMsg & msg)
  {
    decode_msg(msg);
  }

  void encode_msg(TBoard::TCanIntf::TMsg & msg)
  {
    encode_buf(can_msg_get_payload(msg).data());
  }

  void decode_msg(const TBoard::TCanIntf::TMsg & msg)
  {
    decode_buf(can_msg_get_payload(msg).data());
  }
#endif

  /// \brief Encoders data to the buffer to send over CAN
  /// \param buf: pointer to the buffer
  void encode_buf(uint8_t * buf) const
  {
    can_set_signal_raw<uint8_t>(buf, Opcode, 0, 8, true);
    can_set_signal_raw<uint16_t>(buf, Endpoint_ID, 8, 16, true);
    can_set_signal_raw<uint8_t>(buf, Reserved, 24, 8, true);
    can_set_signal_raw<T>(buf, Value, 32, 32, true);
  }

  /// \brief Decoders data from the buffer and saves to struct message
  /// \param buf: pointer to the buffer
  void decode_buf(const uint8_t * buf)
  {
    Opcode = can_get_signal_raw<uint8_t>(buf, 0, 8, true);
    Endpoint_ID = can_get_signal_raw<uint16_t>(buf, 8, 16, true);
    Reserved = can_get_signal_raw<uint8_t>(buf, 24, 8, true);
    Value = can_get_signal_raw<T>(buf, 32, 32, true);
  }

  static const uint8_t cmd_id = 0x04;
  static const uint8_t msg_length = 8;

  uint8_t Opcode = 1;
  uint16_t Endpoint_ID = 0;
  uint8_t Reserved = 0;
  // This may need to become a class T? or have an extra variable that tracks what type it is
  // then we set several value variables that change encode and decode based on the type
  T Value;
};

/// \brief Structure for storing information about parameters
template<typename T>
struct Param
{
  String name;
  uint16_t endpoint_id;
  T value;
};

// https://odrive-cdn.nyc3.digitaloceanspaces.com/releases/firmware/laZ44T35qb_uR6AW6S5RdTrOL9sqZlc2_FonY3vm21Q/flat_endpoints.json
std::vector<Param<float>> fconfig_params({
  Param<float>{"spinout_mechanical_power_threshold", 420, -100.0},
  Param<float>{"spinout_eletrical_power_threshold", 421, 100.0},
  Param<float>{"max_regen_current", 139, 50.0},
  Param<float>{"dc_max_negative_current", 143, -50.0},
  Param<float>{"pos_gain", 400, 100},
  Param<float>{"vel_gain", 401, 12},
  Param<float>{"vel_integrator_gain", 402, 0.0},
  Param<float>{"torque_soft_min", 267, -10.0},
  Param<float>{"torque_soft_max", 268, 10.0},
  // Param<float>{"pos_vel_mapper.offset", 467, 0.0},
  // Param<float>{"pos_vel_mapper.approx_init_pos", 469, 0.0},
  Param<float>{"calib_scan_dist", 215, 4.0},
  Param<float>{"motor_thermistor.config.r_ref", 352, 10000},
  Param<float>{"motor_thermistor.config.t_ref", 353, 25},
  Param<float>{"motor_thermistor.config.beta", 354, 3892},
  Param<float>{"motor_thermistor.config.temp_limit_lower", 355, 60},
  Param<float>{"motor_thermistor.config.temp_limit_upper", 356, 90},
  Param<float>{"vel_limit", 404, 30.0},
  Param<float>{"vel_limit_tolerance", 405, 1.5},
});

std::vector<Param<uint32_t>> bconfig_params({
  // Param<uint32_t>{"anticogging.enabled", 304, 1},
  // Param<uint32_t>{"pos_vel_mapper.offset_valid", 466, 1},
  // Param<uint32_t>{"pos_vel_mapper.approx_init_pos_valid", 468, 1},
  // Param<uint32_t>{"absolute_setpoints", 410, 1},
  Param<uint32_t>{"version_msg_rate_ms", 248, 0},
  Param<uint32_t>{"iq_msg_rate_ms", 251, 0},
  Param<uint32_t>{"bus_voltage_msg_rate_ms", 254, 0},
  Param<uint32_t>{"powers_msg_rate_ms", 256, 0},
  Param<uint32_t>{"gpio7_mode", 159, 3},   // set gpio7 (them+) to analog input mode
  Param<uint32_t>{"motor_thermistor.config.enabled", 357, 0}, // disable motor thermistor
  Param<uint32_t>{"can.temperature_msg_rate_ms", 253, 100},
  Param<uint32_t>{"enable_vel_limit", 393, 1},
  Param<uint32_t>{"enable_torque_mode_vel_limit", 394, 1},
  Param<uint32_t>{"can.encoder_msg_rate_ms", 252, 10},  // Send encoder updates every 10ms
});

std::vector<Param<float>> fanticogging_config_params(
  {Param<float>{"spinout_mechanical_power_threshold", 420, -100.0},
    Param<float>{"spinout_eletrical_power_threshold", 421, 100.0},
    Param<float>{"max_regen_current", 139, 50.0},
    Param<float>{"dc_max_negative_current", 143, -50.0},
    Param<float>{"pos_gain", 400, 20.0},
    Param<float>{"vel_gain", 401, 8.5e-3},
    Param<float>{"vel_integrator_gain", 402, 0.0},
    Param<float>{"torque_soft_min", 267, -150.0},
    Param<float>{"torque_soft_max", 268, 150.0},
    Param<float>{"anticogging.max_torque", 305, 0.15},
    Param<float>{"anticogging.calib_start_vel", 306, 1},
    Param<float>{"anticogging.calib_end_val", 307, 0.15},
    Param<float>{"anticogging.calib_coarse_integrator_gain", 311, 1}});

std::vector<Param<uint32_t>> banticogging_config_params(
  {Param<uint32_t>{"circular_setpoints", 408, true},
    Param<uint32_t>{"offset_valid", 466, true}});

auto benable_config_param = Param<uint32_t>{"anticogging.enabled", 304, true};

/// \brief Message struct for reboooting Odrive
struct Set_Reboot_msg_t final
{
  constexpr Set_Reboot_msg_t() = default;

#ifdef ODRIVE_CAN_MSG_TYPE
  Set_Reboot_msg_t(const TBoard::TCanIntf::TMsg & msg)
  {
    decode_msg(msg);
  }

  void encode_msg(TBoard::TCanIntf::TMsg & msg)
  {
    encode_buf(can_msg_get_payload(msg).data());
  }

  void decode_msg(const TBoard::TCanIntf::TMsg & msg)
  {
    decode_buf(can_msg_get_payload(msg).data());
  }
#endif

  /// \brief Encoders data to the buffer to send over CAN
  /// \param buf: pointer to the buffer
  void encode_buf(uint8_t * buf) const
  {
    can_set_signal_raw<uint8_t>(buf, Action, 0, 8, true);
  }

  /// \brief Decoders data from the buffer and saves to struct message
  /// \param buf: pointer to the buffer
  void decode_buf(const uint8_t * buf)
  {
    Action = can_get_signal_raw<uint8_t>(buf, 0, 8, true);
  }

  static const uint8_t cmd_id = 0x16;
  static const uint8_t msg_length = 8;

  uint8_t Action = 0;   // 0: Reboot, 1: Save Config, 2: Erase Config
};

#endif
