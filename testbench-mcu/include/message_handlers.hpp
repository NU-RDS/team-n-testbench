#ifndef __MESSAGE_HANDLERS_H__
#define __MESSAGE_HANDLERS_H__

#include <rdscom.hpp>
#include "message_definitions.hpp"
#include "user_command.hpp"

namespace msgs {

/// @brief Class to handle incoming messages from the communication interface.
/// This class registers callbacks with a CommunicationInterface and dispatches
/// incoming messages to the appropriate handler functions.
class MessageHandlers {
public:
    /// @brief Constructs a MessageHandlers object.
    /// @param com Reference to the CommunicationInterface.
    /// @param commandBuffer Reference to the UserCommandBuffer for scheduling commands.
    MessageHandlers(rdscom::CommunicationInterface &com, UserCommandBuffer &commandBuffer);

    ///@brief Register all message prototypes
    void registerPrototypes();

    /// @brief Registers all message handlers with the communication interface.
    void addHandlers();

private:
    rdscom::CommunicationInterface &_com;  ///< Reference to the communication interface.
    UserCommandBuffer &_commandBuffer;       ///< Reference to the command buffer.
    bool _isSensorDatastreamActive;          ///< Indicates if the sensor datastream is active.

    /// @brief Handler for Heartbeat messages.
    /// @param msg The received Heartbeat message.
    void onHeartbeatMessage(const rdscom::Message &msg);

    /// @brief Handler for MotorControl messages.
    /// @param msg The received MotorControl message.
    void onMotorControlMessage(const rdscom::Message &msg);

    /// @brief Handler for MotorEvent messages.
    /// @param msg The received MotorEvent message.
    void onMotorEventMessage(const rdscom::Message &msg);

    /// @brief Handler for ControlGo messages.
    /// @param msg The received ControlGo message.
    void onControlGoMessage(const rdscom::Message &msg);

    /// @brief Handler for ControlDone messages.
    /// @param msg The received ControlDone message.
    void onControlDoneMessage(const rdscom::Message &msg);

    /// @brief Handler for StartSensorDatastream messages.
    /// @param msg The received StartSensorDatastream message.
    void onStartSensorDatastreamMessage(const rdscom::Message &msg);

    /// @brief Handler for SensorDatastream messages.
    /// @param msg The received SensorDatastream message.
    void onSensorDatastreamMessage(const rdscom::Message &msg);

    /// @brief Handler for StopSensorDatastream messages.
    /// @param msg The received StopSensorDatastream message.
    void onStopSensorDatastreamMessage(const rdscom::Message &msg);

    /// @brief Handler for ClearControlQueue messages.
    /// @param msg The received ClearControlQueue message.
    void onClearControlQueueMessage(const rdscom::Message &msg);

    /// @brief Handler for Error messages.
    /// @param msg The received Error message.
    void onErrorMessage(const rdscom::Message &msg);

    /// @brief Handler for Stop messages.
    /// @param msg The received Stop message.
    void onStopMessage(const rdscom::Message &msg);
};

} // namespace msgs

#endif  // __MESSAGE_HANDLERS_H__
