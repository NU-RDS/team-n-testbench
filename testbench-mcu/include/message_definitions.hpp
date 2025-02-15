#ifndef MESSAGE_DEFINITIONS_HPP
#define MESSAGE_DEFINITIONS_HPP

#include "rdscom.hpp"

namespace msgs {

// --- DataPrototypes ---

// DataPrototype 0: Heartbeat
inline rdscom::DataPrototype heartbeatProto() {
    rdscom::DataPrototype proto(0);
    proto.addField("rand", rdscom::DataFieldType::INT8);
    return proto;
}

// DataPrototype 1: MotorControl
inline rdscom::DataPrototype motorControlProto() {
    rdscom::DataPrototype proto(1);
    proto.addField("motor_id", rdscom::DataFieldType::UINT8);
    proto.addField("control_mode", rdscom::DataFieldType::UINT8);
    proto.addField("control_value", rdscom::DataFieldType::FLOAT);
    proto.addField("simutaneous", rdscom::DataFieldType::BOOL);
    return proto;
}

// DataPrototype 2: MotorEvent
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

// DataPrototype 3: ControlGo
inline rdscom::DataPrototype controlGoProto() {
    rdscom::DataPrototype proto(3);
    proto.addField("rand", rdscom::DataFieldType::INT8);
    return proto;
}

// DataPrototype 4: ControlDone
inline rdscom::DataPrototype controlDoneProto() {
    rdscom::DataPrototype proto(4);
    proto.addField("success", rdscom::DataFieldType::BOOL);
    proto.addField("time", rdscom::DataFieldType::UINT32);
    proto.addField("executed", rdscom::DataFieldType::UINT8);
    return proto;
}

// DataPrototype 5: StartSensorDatastream
inline rdscom::DataPrototype startSensorDataStreamProto() {
    rdscom::DataPrototype proto(5);
    proto.addField("sensor_id", rdscom::DataFieldType::UINT8);
    proto.addField("frequency", rdscom::DataFieldType::UINT8);
    return proto;
}

// DataPrototype 6: SensorDatastream
inline rdscom::DataPrototype sensorDatastreamProto() {
    rdscom::DataPrototype proto(6);
    proto.addField("sensor_id", rdscom::DataFieldType::UINT8);
    proto.addField("data", rdscom::DataFieldType::FLOAT);
    return proto;
}

// DataPrototype 7: StopSensorDatastream
inline rdscom::DataPrototype stopSensorDatastreamProto() {
    rdscom::DataPrototype proto(7);
    proto.addField("sensor_id", rdscom::DataFieldType::UINT8);
    return proto;
}

// DataPrototype 8: ClearControlQueue
inline rdscom::DataPrototype clearControlQueueProto() {
    rdscom::DataPrototype proto(8);
    proto.addField("rand", rdscom::DataFieldType::INT8);
    return proto;
}

// DataPrototype 9: Error
inline rdscom::DataPrototype errorMessageProto() {
    rdscom::DataPrototype proto(9);
    proto.addField("error_code", rdscom::DataFieldType::UINT8);
    return proto;
}

// DataPrototype 10: Stop
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

// --- Factory Methods to Build Messages ---

inline rdscom::Message createHeartbeatMessage(rdscom::MessageType msgType, std::int8_t randVal) {
    rdscom::Message msg(msgType, heartbeatProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

inline rdscom::Message createMotorControlMessage(rdscom::MessageType msgType,
                                                 std::uint8_t motor_id,
                                                 std::uint8_t control_mode,
                                                 float control_value,
                                                 bool simultaneous) {
    rdscom::Message msg(msgType, motorControlProto());
    msg.setField<std::uint8_t>("motor_id", motor_id);
    msg.setField<std::uint8_t>("control_mode", control_mode);
    msg.setField<float>("control_value", control_value);
    msg.setField<bool>("simutaneous", simultaneous);
    return msg;
}

inline rdscom::Message createMotorEventMessage(rdscom::MessageType msgType,
                                               std::uint8_t motor_id,
                                               bool success,
                                               std::uint8_t event_type,
                                               float event_value,
                                               std::uint8_t num_in_queue,
                                               std::uint8_t executed_with_count) {
    rdscom::Message msg(msgType, motorEventProto());
    msg.setField<std::uint8_t>("motor_id", motor_id);
    msg.setField<bool>("success", success);
    msg.setField<std::uint8_t>("event_type", event_type);
    msg.setField<float>("event_value", event_value);
    msg.setField<std::uint8_t>("num_in_queue", num_in_queue);
    msg.setField<std::uint8_t>("executed_with_count", executed_with_count);
    return msg;
}

inline rdscom::Message createControlGoMessage(rdscom::MessageType msgType, std::int8_t randVal) {
    rdscom::Message msg(msgType, controlGoProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

inline rdscom::Message createControlDoneMessage(rdscom::MessageType msgType,
                                                bool success,
                                                std::uint32_t time,
                                                std::uint8_t executed) {
    rdscom::Message msg(msgType, controlDoneProto());
    msg.setField<bool>("success", success);
    msg.setField<std::uint32_t>("time", time);
    msg.setField<std::uint8_t>("executed", executed);
    return msg;
}

inline rdscom::Message createStartSensorDatastreamMessage(rdscom::MessageType msgType,
                                                          std::uint8_t sensor_id,
                                                          std::uint8_t frequency) {
    rdscom::Message msg(msgType, startSensorDataStreamProto());
    msg.setField<std::uint8_t>("sensor_id", sensor_id);
    msg.setField<std::uint8_t>("frequency", frequency);
    return msg;
}

inline rdscom::Message createSensorDatastreamMessage(rdscom::MessageType msgType,
                                                     std::uint8_t sensor_id,
                                                     float data) {
    rdscom::Message msg(msgType, sensorDatastreamProto());
    msg.setField<std::uint8_t>("sensor_id", sensor_id);
    msg.setField<float>("data", data);
    return msg;
}

inline rdscom::Message createStopSensorDatastreamMessage(rdscom::MessageType msgType,
                                                         std::uint8_t sensor_id) {
    rdscom::Message msg(msgType, stopSensorDatastreamProto());
    msg.setField<std::uint8_t>("sensor_id", sensor_id);
    return msg;
}

inline rdscom::Message createClearControlQueueMessage(rdscom::MessageType msgType, std::int8_t randVal) {
    rdscom::Message msg(msgType, clearControlQueueProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

inline rdscom::Message createErrorMessage(rdscom::MessageType msgType, std::uint8_t error_code) {
    rdscom::Message msg(msgType, errorMessageProto());
    msg.setField<std::uint8_t>("error_code", error_code);
    return msg;
}

inline rdscom::Message createStopMessage(rdscom::MessageType msgType, std::int8_t randVal) {
    rdscom::Message msg(msgType, stopProto());
    msg.setField<std::int8_t>("rand", randVal);
    return msg;
}

}  // namespace msgs

#endif  // MESSAGE_DEFINITIONS_HPP
