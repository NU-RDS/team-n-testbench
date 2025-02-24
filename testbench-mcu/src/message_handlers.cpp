#include "message_handlers.hpp"
#include "message_definitions.hpp"
#include <iostream>
#include <map>
#include <rdscom.hpp>

namespace msgs {

MessageHandlers::MessageHandlers(rdscom::CommunicationInterface &com, UserCommandBuffer &commandBuffer)
    : _com(com), _commandBuffer(commandBuffer), _isSensorDatastreamActive(false) {
}

///@brief Register all message prototypes
void MessageHandlers::registerPrototypes() {
    _com.addPrototype(msgs::heartbeatProto());
    _com.addPrototype(msgs::motorControlProto());
    _com.addPrototype(msgs::motorEventProto());
    _com.addPrototype(msgs::controlGoProto());
    _com.addPrototype(msgs::controlDoneProto());
    _com.addPrototype(msgs::startSensorDataStreamProto());
    _com.addPrototype(msgs::sensorDataStreamProto());
    _com.addPrototype(msgs::stopSensorDataStreamProto());
    _com.addPrototype(msgs::clearControlQueueProto());
    _com.addPrototype(msgs::errorProto());
    _com.addPrototype(msgs::stopProto());
}

/// @brief Registers all message handlers with the communication interface.
void MessageHandlers::addHandlers() {
    _com.addCallback(heartbeatId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onHeartbeatMessage(msg); });
    _com.addCallback(motorControlId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onMotorControlMessage(msg); });
    _com.addCallback(motorEventId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onMotorEventMessage(msg); });
    _com.addCallback(controlGoId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onControlGoMessage(msg); });
    _com.addCallback(controlDoneId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onControlDoneMessage(msg); });
    _com.addCallback(startSensorDatastreamId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onStartSensorDatastreamMessage(msg); });
    _com.addCallback(sensorDatastreamId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onSensorDatastreamMessage(msg); });
    _com.addCallback(stopSensorDatastreamId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onStopSensorDatastreamMessage(msg); });
    _com.addCallback(clearControlQueueId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onClearControlQueueMessage(msg); });
    _com.addCallback(errorId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onErrorMessage(msg); });
    _com.addCallback(stopId(), rdscom::MessageType::REQUEST,
        [this](const rdscom::Message &msg) { this->onStopMessage(msg); });
}

/// @brief Handler for Heartbeat messages.
void MessageHandlers::onHeartbeatMessage(const rdscom::Message &msg) {
    std::int8_t randVal = msg.getField<std::int8_t>("rand").value();
    rdscom::Message response = rdscom::Message::createResponse(msg, msgs::heartbeatProto());
    response.setField<std::int8_t>("rand", randVal);
    _com.sendMessage(response);
}

/// @brief Handler for MotorControl messages.
void MessageHandlers::onMotorControlMessage(const rdscom::Message &msg) {
    auto result = FingerControlCommand::fromMessage(msg);
    if (!result) {
        std::cerr << "Error parsing MotorControl message\n";
        rdscom::Message response = rdscom::Message::createResponse(msg, msgs::motorControlProto());
        return;
    }

    FingerControlCommand command = result.value();
    _commandBuffer.addCommand(std::make_shared<FingerControlCommand>(command));
    rdscom::Message response = createMotorControlMessageResponse(
        msg,
        command.fingerJoinID(),
        static_cast<std::uint8_t>(command.controlType()),
        command.controlValue(),
        command.simultaneous()
    );
    _com.sendMessage(response, true);
}

/// @brief Handler for MotorEvent messages.
void MessageHandlers::onMotorEventMessage(const rdscom::Message &msg) {
    msg.printClean(std::cout);
}

/// @brief Handler for ControlGo messages.
void MessageHandlers::onControlGoMessage(const rdscom::Message &msg) {
    _commandBuffer.executeCurrentCommandSlice();
}

/// @brief Handler for ControlDone messages.
void MessageHandlers::onControlDoneMessage(const rdscom::Message &msg) {
    msg.printClean(std::cout);
}

/// @brief Handler for StartSensorDatastream messages.
void MessageHandlers::onStartSensorDatastreamMessage(const rdscom::Message &msg) {
    _isSensorDatastreamActive = true;
    rdscom::Message response = createStartSensorDatastreamMessageResponse(
        msg,
        msg.getField<std::uint8_t>("sensor_id").value(),
        msg.getField<std::uint8_t>("frequency").value()
    );
    _com.sendMessage(response, true);
}

/// @brief Handler for SensorDatastream messages.
void MessageHandlers::onSensorDatastreamMessage(const rdscom::Message &msg) {
    msg.printClean(std::cout);
}

/// @brief Handler for StopSensorDatastream messages.
void MessageHandlers::onStopSensorDatastreamMessage(const rdscom::Message &msg) {
    _isSensorDatastreamActive = false;
    rdscom::Message response = createStopSensorDatastreamMessageResponse(
        msg,
        msg.getField<std::uint8_t>("sensor_id").value()
    );

    _com.sendMessage(response, true);
}

/// @brief Handler for ClearControlQueue messages.
void MessageHandlers::onClearControlQueueMessage(const rdscom::Message &msg) {
    _commandBuffer.clear();
    rdscom::Message response = createClearControlQueueMessageResponse(
        msg,
        msg.getField<std::int8_t>("rand").value()
    );

    _com.sendMessage(response, true);
}

/// @brief Handler for Error messages.
void MessageHandlers::onErrorMessage(const rdscom::Message &msg) {
    msg.printClean(std::cerr);
}

/// @brief Handler for Stop messages.
void MessageHandlers::onStopMessage(const rdscom::Message &msg) {
    _commandBuffer.clear();
    rdscom::Message response = createStopMessageResponse(
        msg,
        msg.getField<std::int8_t>("rand").value()
    );
    _com.sendMessage(response, true);
}

} // namespace msgs
