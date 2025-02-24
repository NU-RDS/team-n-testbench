#ifndef MESSAGE_DEFINITIONS_HPP
#define MESSAGE_DEFINITIONS_HPP

#include "rdscom.hpp"

namespace msgs {

// --- DataPrototypes ---

/// @brief Returns the Heartbeat DataPrototype (ID: 0).
inline rdscom::DataPrototype heartbeatProto() {
    rdscom::DataPrototype proto(0);
    proto.addField("rand", rdscom::DataFieldType::INT8);
    return proto;
}

/// @brief Returns the MotorControl DataPrototype (ID: 1).
inline rdscom::DataPrototype motorControlProto() {
    rdscom::DataPrototype proto(1);
    proto.addField("motor_id", rdscom::DataFieldType::UINT8);
    proto.addField("control_mode", rdscom::DataFieldType::UINT8);
    proto.addField("control_value", rdscom::DataFieldType::FLOAT);
    proto.addField("simultaneous", rdscom::DataFieldType::BOOL);
    return proto;
}

/// @brief Returns the MotorEvent DataPrototype (ID: 2).
inline rdscom::DataPrototype motorEventProto() {
    rdscom::DataPrototype proto(2);
    proto.addField("motor_id", rdscom::DataFieldType::UINT8);
    proto.addField("success", rdscom::DataFieldType::BOOL);
    proto.addField("event_type", rdscom::DataFieldType::UINT8);
    proto.addField("event_value", rdscom::DataFieldType::FLOAT);
    proto.addField("num_in_queue", rdscom::DataFieldType::UINT8);
    proto.addField("executed_with_count", rdscom::DataFieldType::UINT8);
    return proto;
}

/// @brief Returns the ControlGo DataPrototype (ID: 3).
inline rdscom::DataPrototype controlGoProto() {
    rdscom::DataPrototype proto(3);
    proto.addField("rand", rdscom::DataFieldType::INT8);
    return proto;
}

/// @brief Returns the ControlDone DataPrototype (ID: 4).
inline rdscom::DataPrototype controlDoneProto() {
    rdscom::DataPrototype proto(4);
    proto.addField("success", rdscom::DataFieldType::BOOL);
    proto.addField("time", rdscom::DataFieldType::UINT32);
    proto.addField("executed", rdscom::DataFieldType::UINT8);
    return proto;
}

/// @brief Returns the StartSensorDatastream DataPrototype (ID: 5).
inline rdscom::DataPrototype startSensorDataStreamProto() {
    rdscom::DataPrototype proto(5);
    proto.addField("sensor_id", rdscom::DataFieldType::UINT8);
    proto.addField("frequency", rdscom::DataFieldType::UINT8);
    return proto;
}

/// @brief Returns the SensorDatastream DataPrototype (ID: 6).
inline rdscom::DataPrototype sensorDataStreamProto() {
    rdscom::DataPrototype proto(6);
    proto.addField("sensor_id", rdscom::DataFieldType::UINT8);
    proto.addField("data", rdscom::DataFieldType::FLOAT);
    return proto;
}

/// @brief Returns the StopSensorDatastream DataPrototype (ID: 7).
inline rdscom::DataPrototype stopSensorDataStreamProto() {
    rdscom::DataPrototype proto(7);
    proto.addField("sensor_id", rdscom::DataFieldType::UINT8);
    return proto;
}

/// @brief Returns the ClearControlQueue DataPrototype (ID: 8).
inline rdscom::DataPrototype clearControlQueueProto() {
    rdscom::DataPrototype proto(8);
    proto.addField("rand", rdscom::DataFieldType::INT8);
    return proto;
}

/// @brief Returns the Error DataPrototype (ID: 9).
inline rdscom::DataPrototype errorProto() {
    rdscom::DataPrototype proto(9);
    proto.addField("error_code", rdscom::DataFieldType::UINT8);
    return proto;
}

/// @brief Returns the Stop DataPrototype (ID: 10).
inline rdscom::DataPrototype stopProto() {
    rdscom::DataPrototype proto(10);
    proto.addField("rand", rdscom::DataFieldType::INT8);
    return proto;
}

// --- Utility Functions for Getting Message IDs (thisTypeOfCase) ---

inline std::uint8_t heartbeatId() { return 0; }
inline std::uint8_t motorControlId() { return 1; }
inline std::uint8_t motorEventId() { return 2; }
inline std::uint8_t controlGoId() { return 3; }
inline std::uint8_t controlDoneId() { return 4; }
inline std::uint8_t startSensorDatastreamId() { return 5; }
inline std::uint8_t sensorDatastreamId() { return 6; }
inline std::uint8_t stopSensorDatastreamId() { return 7; }
inline std::uint8_t clearControlQueueId() { return 8; }
inline std::uint8_t errorId() { return 9; }
inline std::uint8_t stopId() { return 10; }

// --- Factory Methods to Build Request Messages ---
// Request functions no longer take a MessageType parameter,
// always using rdscom::MessageType::REQUEST.

/// @brief Creates a Heartbeat Request message.
/// @param randVal The INT8 value for connectivity check.
/// @return A Heartbeat Message object.
inline rdscom::Message createHeartbeatMessageRequest(std::int8_t randVal) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, heartbeatProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

/// @brief Creates a MotorControl Request message.
/// @param motor_id Motor identifier (UINT8).
/// @param control_mode Control mode (UINT8).
/// @param control_value Control value (FLOAT).
/// @param simultaneous Whether control is simultaneous.
/// @return A MotorControl Message object.
inline rdscom::Message createMotorControlMessageRequest(std::uint8_t motor_id,
                                                         std::uint8_t control_mode,
                                                         float control_value,
                                                         bool simultaneous) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, motorControlProto());
    msg.setField<std::uint8_t>("motor_id", motor_id);
    msg.setField<std::uint8_t>("control_mode", control_mode);
    msg.setField<float>("control_value", control_value);
    msg.setField<std::uint8_t>("simultaneous", simultaneous ? 1 : 0);
    return msg;
}

/// @brief Creates a MotorEvent Request message.
/// @param motor_id Motor identifier (UINT8).
/// @param success Whether the event was successful.
/// @param event_type Event type (UINT8).
/// @param event_value Event value (FLOAT).
/// @param num_in_queue Number in queue (UINT8).
/// @param executed_with_count Number executed with count (UINT8).
/// @return A MotorEvent Message object.
inline rdscom::Message createMotorEventMessageRequest(std::uint8_t motor_id,
                                                       bool success,
                                                       std::uint8_t event_type,
                                                       float event_value,
                                                       std::uint8_t num_in_queue,
                                                       std::uint8_t executed_with_count) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, motorEventProto());
    msg.setField<std::uint8_t>("motor_id", motor_id);
    msg.setField<std::uint8_t>("success", success ? 1 : 0);
    msg.setField<std::uint8_t>("event_type", event_type);
    msg.setField<float>("event_value", event_value);
    msg.setField<std::uint8_t>("num_in_queue", num_in_queue);
    msg.setField<std::uint8_t>("executed_with_count", executed_with_count);
    return msg;
}

/// @brief Creates a ControlGo Request message.
/// @param randVal The INT8 random value.
/// @return A ControlGo Message object.
inline rdscom::Message createControlGoMessageRequest(std::int8_t randVal) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, controlGoProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

/// @brief Creates a ControlDone Request message.
/// @param success Whether the operation was successful.
/// @param time Execution time (UINT32).
/// @param executed Number executed (UINT8).
/// @return A ControlDone Message object.
inline rdscom::Message createControlDoneMessageRequest(bool success,
                                                        std::uint32_t time,
                                                        std::uint8_t executed) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, controlDoneProto());
    msg.setField<std::uint8_t>("success", success ? 1 : 0);
    msg.setField<std::uint32_t>("time", time);
    msg.setField<std::uint8_t>("executed", executed);
    return msg;
}

/// @brief Creates a StartSensorDatastream Request message.
/// @param sensor_id Sensor identifier (UINT8).
/// @param frequency Frequency in Hz (UINT8).
/// @return A StartSensorDatastream Message object.
inline rdscom::Message createStartSensorDatastreamMessageRequest(std::uint8_t sensor_id,
                                                                  std::uint8_t frequency) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, startSensorDataStreamProto());
    msg.setField<std::uint8_t>("sensor_id", sensor_id);
    msg.setField<std::uint8_t>("frequency", frequency);
    return msg;
}

/// @brief Creates a SensorDatastream Request message.
/// @param sensor_id Sensor identifier (UINT8).
/// @param data Sensor data (FLOAT).
/// @return A SensorDatastream Message object.
inline rdscom::Message createSensorDatastreamMessageRequest(std::uint8_t sensor_id,
                                                             float data) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, sensorDataStreamProto());
    msg.setField<std::uint8_t>("sensor_id", sensor_id);
    msg.setField<float>("data", data);
    return msg;
}

/// @brief Creates a StopSensorDatastream Request message.
/// @param sensor_id Sensor identifier (UINT8).
/// @return A StopSensorDatastream Message object.
inline rdscom::Message createStopSensorDatastreamMessageRequest(std::uint8_t sensor_id) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, stopSensorDataStreamProto());
    msg.setField<std::uint8_t>("sensor_id", sensor_id);
    return msg;
}

/// @brief Creates a ClearControlQueue Request message.
/// @param randVal The INT8 random value.
/// @return A ClearControlQueue Message object.
inline rdscom::Message createClearControlQueueMessageRequest(std::int8_t randVal) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, clearControlQueueProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

/// @brief Creates an Error Request message.
/// @param error_code The error code (UINT8).
/// @return An Error Message object.
inline rdscom::Message createErrorMessageRequest(std::uint8_t error_code) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, errorProto());
    msg.setField<std::uint8_t>("error_code", error_code);
    return msg;
}

/// @brief Creates a Stop Request message.
/// @param randVal The INT8 random value.
/// @return A Stop Message object.
inline rdscom::Message createStopMessageRequest(std::int8_t randVal) {
    rdscom::Message msg(rdscom::MessageType::REQUEST, stopProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

// --- Factory Methods to Build Response Messages ---
// Each function creates a response message using Message::createResponse().

/// @brief Creates a Heartbeat Response message based on a request.
/// @param request The original request message.
/// @param randVal The INT8 value to echo.
/// @return A Heartbeat Response message.
inline rdscom::Message createHeartbeatMessageResponse(const rdscom::Message &request, std::int8_t randVal) {
    rdscom::Message response = rdscom::Message::createResponse(request, heartbeatProto());
    response.setField<std::int8_t>("rand", randVal);
    return response;
}

/// @brief Creates a MotorControl Response message based on a request.
/// @param request The original request message.
/// @param motor_id The motor identifier (UINT8).
/// @param control_mode The control mode (UINT8).
/// @param control_value The control value (FLOAT).
/// @param simultaneous Whether the control is simultaneous.
/// @return A MotorControl Response message.
inline rdscom::Message createMotorControlMessageResponse(const rdscom::Message &request,
                                                           std::uint8_t motor_id,
                                                           std::uint8_t control_mode,
                                                           float control_value,
                                                           bool simultaneous) {
    rdscom::Message response = rdscom::Message::createResponse(request, motorControlProto());
    response.setField<std::uint8_t>("motor_id", motor_id);
    response.setField<std::uint8_t>("control_mode", control_mode);
    response.setField<float>("control_value", control_value);
    response.setField<std::int8_t>("simultaneous", simultaneous ? 1 : 0);
    return response;
}

/// @brief Creates a MotorEvent Response message based on a request.
/// @param request The original request message.
/// @param motor_id The motor identifier (UINT8).
/// @param success Whether the event was successful.
/// @param event_type The event type (UINT8).
/// @param event_value The event value (FLOAT).
/// @param num_in_queue Number in queue (UINT8).
/// @param executed_with_count Number executed with count (UINT8).
/// @return A MotorEvent Response message.
inline rdscom::Message createMotorEventMessageResponse(const rdscom::Message &request,
                                                         std::uint8_t motor_id,
                                                         bool success,
                                                         std::uint8_t event_type,
                                                         float event_value,
                                                         std::uint8_t num_in_queue,
                                                         std::uint8_t executed_with_count) {
    rdscom::Message response = rdscom::Message::createResponse(request, motorEventProto());
    response.setField<std::uint8_t>("motor_id", motor_id);
    response.setField<std::uint8_t>("success", success ? 1 : 0);
    response.setField<std::uint8_t>("event_type", event_type);
    response.setField<float>("event_value", event_value);
    response.setField<std::uint8_t>("num_in_queue", num_in_queue);
    response.setField<std::uint8_t>("executed_with_count", executed_with_count);
    return response;
}

/// @brief Creates a ControlGo Response message based on a request.
/// @param request The original request message.
/// @param randVal The INT8 random value.
/// @return A ControlGo Response message.
inline rdscom::Message createControlGoMessageResponse(const rdscom::Message &request, std::int8_t randVal) {
    rdscom::Message response = rdscom::Message::createResponse(request, controlGoProto());
    response.setField<std::int8_t>("rand", randVal);
    return response;
}

/// @brief Creates a ControlDone Response message based on a request.
/// @param request The original request message.
/// @param success Whether the control queue executed successfully.
/// @param time_val Execution time (UINT32).
/// @param executed Number executed (UINT8).
/// @return A ControlDone Response message.
inline rdscom::Message createControlDoneMessageResponse(const rdscom::Message &request,
                                                          bool success,
                                                          std::uint32_t time_val,
                                                          std::uint8_t executed) {
    rdscom::Message response = rdscom::Message::createResponse(request, controlDoneProto());
    response.setField<std::uint8_t>("success", success ? 1 : 0);
    response.setField<std::uint32_t>("time", time_val);
    response.setField<std::uint8_t>("executed", executed);
    return response;
}

/// @brief Creates a StartSensorDatastream Response message based on a request.
/// @param request The original request message.
/// @param sensor_id The sensor identifier (UINT8).
/// @param frequency The frequency (UINT8).
/// @return A StartSensorDatastream Response message.
inline rdscom::Message createStartSensorDatastreamMessageResponse(const rdscom::Message &request,
                                                                    std::uint8_t sensor_id,
                                                                    std::uint8_t frequency) {
    rdscom::Message response = rdscom::Message::createResponse(request, startSensorDataStreamProto());
    response.setField<std::uint8_t>("sensor_id", sensor_id);
    response.setField<std::uint8_t>("frequency", frequency);
    return response;
}

/// @brief Creates a SensorDatastream Response message based on a request.
/// @param request The original request message.
/// @param sensor_id The sensor identifier (UINT8).
/// @param data The sensor data (FLOAT).
/// @return A SensorDatastream Response message.
inline rdscom::Message createSensorDatastreamMessageResponse(const rdscom::Message &request,
                                                               std::uint8_t sensor_id,
                                                               float data) {
    rdscom::Message response = rdscom::Message::createResponse(request, sensorDataStreamProto());
    response.setField<std::uint8_t>("sensor_id", sensor_id);
    response.setField<float>("data", data);
    return response;
}

/// @brief Creates a StopSensorDatastream Response message based on a request.
/// @param request The original request message.
/// @param sensor_id The sensor identifier (UINT8).
/// @return A StopSensorDatastream Response message.
inline rdscom::Message createStopSensorDatastreamMessageResponse(const rdscom::Message &request,
                                                                   std::uint8_t sensor_id) {
    rdscom::Message response = rdscom::Message::createResponse(request, stopSensorDataStreamProto());
    response.setField<std::uint8_t>("sensor_id", sensor_id);
    return response;
}

/// @brief Creates a ClearControlQueue Response message based on a request.
/// @param request The original request message.
/// @param randVal The INT8 random value.
/// @return A ClearControlQueue Response message.
inline rdscom::Message createClearControlQueueMessageResponse(const rdscom::Message &request, std::int8_t randVal) {
    rdscom::Message response = rdscom::Message::createResponse(request, clearControlQueueProto());
    response.setField<std::int8_t>("rand", randVal);
    return response;
}

/// @brief Creates an Error Response message based on a request.
/// @param request The original request message.
/// @param error_code The error code (UINT8).
/// @return An Error Response message.
inline rdscom::Message createErrorMessageResponse(const rdscom::Message &request, std::uint8_t error_code) {
    rdscom::Message response = rdscom::Message::createResponse(request, errorProto());
    response.setField<std::uint8_t>("error_code", error_code);
    return response;
}

/// @brief Creates a Stop Response message based on a request.
/// @param request The original request message.
/// @param randVal The INT8 random value.
/// @return A Stop Response message.
inline rdscom::Message createStopMessageResponse(const rdscom::Message &request, std::int8_t randVal) {
    rdscom::Message response = rdscom::Message::createResponse(request, stopProto());
    response.setField<std::int8_t>("rand", randVal);
    return response;
}

}  // namespace msgs

#endif  // MESSAGE_DEFINITIONS_HPP
