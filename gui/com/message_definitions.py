#!/usr/bin/env python3
"""
message_defs.py

This module implements the message definitions for the GUI-MCU protocol,
mirroring the C++ header. It uses the rdscom Python library to define data
prototypes, utility functions for message IDs, and factory methods to build messages.

Each message type is assigned a unique ID and a corresponding DataPrototype.
"""

from rdscom.rdscom import (
    DataPrototype,
    DataFieldType,
    Message,
    MessageType,
)

# --- DataPrototypes ---

class MessageDefinitions:
    @staticmethod
    def all_protos():
        return [
            MessageDefinitions.heartbeat_proto(),
            MessageDefinitions.motor_control_proto(),
            MessageDefinitions.motor_event_proto(),
            MessageDefinitions.control_go_proto(),
            MessageDefinitions.control_done_proto(),
            MessageDefinitions.start_sensor_datastream_proto(),
            MessageDefinitions.sensor_datastream_proto(),
            MessageDefinitions.stop_sensor_datastream_proto(),
            MessageDefinitions.clear_control_queue_proto(),
            MessageDefinitions.error_message_proto(),
            MessageDefinitions.stop_proto(),
        ]
    
    @staticmethod
    def all_proto_ids():
        return [proto.id for proto in MessageDefinitions.all_protos()]


    @staticmethod
    def heartbeat_proto() -> DataPrototype:
        """
        Creates the Heartbeat DataPrototype (ID: 0).

        Fields:
        - "rand": INT8
        """
        proto = DataPrototype(0)
        proto.add_field("rand", DataFieldType.INT8)
        return proto

    @staticmethod
    def motor_control_proto() -> DataPrototype:
        """
        Creates the MotorControl DataPrototype (ID: 1).

        Fields:
        - "motor_id": UINT8
        - "control_mode": UINT8
        - "control_value": FLOAT
        - "simutaneous": BOOL
        """
        proto = DataPrototype(1)
        proto.add_field("motor_id", DataFieldType.UINT8)
        proto.add_field("control_mode", DataFieldType.UINT8)
        proto.add_field("control_value", DataFieldType.FLOAT)
        proto.add_field("simutaneous", DataFieldType.BOOL)
        return proto

    @staticmethod
    def motor_event_proto() -> DataPrototype:
        """
        Creates the MotorEvent DataPrototype (ID: 2).

        Fields:
        - "motor_id": UINT8
        - "success": BOOL
        - "event_type": UINT8
        - "event_value": FLOAT
        - "num_in_queue": UINT8
        - "executed_with_count": UINT8
        """
        proto = DataPrototype(2)
        proto.add_field("motor_id", DataFieldType.UINT8)
        proto.add_field("success", DataFieldType.BOOL)
        proto.add_field("event_type", DataFieldType.UINT8)
        proto.add_field("event_value", DataFieldType.FLOAT)
        proto.add_field("num_in_queue", DataFieldType.UINT8)
        proto.add_field("executed_with_count", DataFieldType.UINT8)
        return proto

    @staticmethod
    def control_go_proto() -> DataPrototype:
        """
        Creates the ControlGo DataPrototype (ID: 3).

        Fields:
        - "rand": INT8
        """
        proto = DataPrototype(3)
        proto.add_field("rand", DataFieldType.INT8)
        return proto

    @staticmethod
    def control_done_proto() -> DataPrototype:
        """
        Creates the ControlDone DataPrototype (ID: 4).

        Fields:
        - "success": BOOL
        - "time": UINT32
        - "executed": UINT8
        """
        proto = DataPrototype(4)
        proto.add_field("success", DataFieldType.BOOL)
        proto.add_field("time", DataFieldType.UINT32)
        proto.add_field("executed", DataFieldType.UINT8)
        return proto

    @staticmethod
    def start_sensor_datastream_proto() -> DataPrototype:
        """
        Creates the StartSensorDatastream DataPrototype (ID: 5).

        Fields:
        - "sensor_id": UINT8
        - "frequency": UINT8
        """
        proto = DataPrototype(5)
        proto.add_field("sensor_id", DataFieldType.UINT8)
        proto.add_field("frequency", DataFieldType.UINT8)
        return proto

    @staticmethod
    def sensor_datastream_proto() -> DataPrototype:
        """
        Creates the SensorDatastream DataPrototype (ID: 6).

        Fields:
        - "sensor_id": UINT8
        - "data": FLOAT
        """
        proto = DataPrototype(6)
        proto.add_field("sensor_id", DataFieldType.UINT8)
        proto.add_field("data", DataFieldType.FLOAT)
        return proto

    @staticmethod
    def stop_sensor_datastream_proto() -> DataPrototype:
        """
        Creates the StopSensorDatastream DataPrototype (ID: 7).

        Fields:
        - "sensor_id": UINT8
        """
        proto = DataPrototype(7)
        proto.add_field("sensor_id", DataFieldType.UINT8)
        return proto

    @staticmethod
    def clear_control_queue_proto() -> DataPrototype:
        """
        Creates the ClearControlQueue DataPrototype (ID: 8).

        Fields:
        - "rand": INT8
        """
        proto = DataPrototype(8)
        proto.add_field("rand", DataFieldType.INT8)
        return proto

    @staticmethod
    def error_message_proto() -> DataPrototype:
        """
        Creates the Error Message DataPrototype (ID: 9).

        Fields:
        - "error_code": UINT8
        """
        proto = DataPrototype(9)
        proto.add_field("error_code", DataFieldType.UINT8)
        return proto

    @staticmethod
    def stop_proto() -> DataPrototype:
        """
        Creates the Stop DataPrototype (ID: 10).

        Fields:
        - "rand": INT8
        """
        proto = DataPrototype(10)
        proto.add_field("rand", DataFieldType.INT8)
        return proto


    # --- Utility Functions for Getting Message IDs (thisTypeOfCase) ---

    @staticmethod
    def heartbeat_id() -> int:
        """Returns the ID for the Heartbeat message (0)."""
        return 0

    @staticmethod
    def motor_control_id() -> int:
        """Returns the ID for the MotorControl message (1)."""
        return 1

    @staticmethod
    def motor_event_id() -> int:
        """Returns the ID for the MotorEvent message (2)."""
        return 2

    @staticmethod
    def control_go_id() -> int:
        """Returns the ID for the ControlGo message (3)."""
        return 3

    @staticmethod
    def control_done_id() -> int:
        """Returns the ID for the ControlDone message (4)."""
        return 4
    
    @staticmethod
    def start_sensor_datastream_id() -> int:
        """Returns the ID for the StartSensorDatastream message (5)."""
        return 5

    @staticmethod
    def sensor_datastream_id() -> int:
        """Returns the ID for the SensorDatastream message (6)."""
        return 6

    @staticmethod
    def stop_sensor_datastream_id() -> int:
        """Returns the ID for the StopSensorDatastream message (7)."""
        return 7

    @staticmethod
    def clear_control_queue_id() -> int:
        """Returns the ID for the ClearControlQueue message (8)."""
        return 8

    @staticmethod
    def error_id() -> int:
        """Returns the ID for the Error message (9)."""
        return 9

    @staticmethod
    def stop_id() -> int:
        """Returns the ID for the Stop message (10)."""
        return 10


    # --- Factory Methods to Build Messages ---

    @staticmethod
    def create_heartbeat_message(msg_type: MessageType, rand_val: int) -> Message:
        """
        Creates a Heartbeat message.

        Args:
        msg_type: The MessageType (e.g. REQUEST, RESPONSE, etc.).
        rand_val: An INT8 value used for checking connectivity.

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.heartbeat_proto())
        msg.set_field("rand", rand_val)
        return msg

    @staticmethod
    def create_motor_control_message(
        msg_type: MessageType,
        motor_id: int,
        control_mode: int,
        control_value: float,
        simultaneous: bool,
    ) -> Message:
        """
        Creates a MotorControl message.

        Args:
        msg_type: The MessageType.
        motor_id: The motor identifier (UINT8).
        control_mode: The control mode (UINT8).
        control_value: The control value (FLOAT).
        simultaneous: Whether to execute simultaneously (BOOL).

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.motor_control_proto())
        msg.set_field("motor_id", motor_id)
        msg.set_field("control_mode", control_mode)
        msg.set_field("control_value", control_value)
        msg.set_field("simutaneous", simultaneous)
        return msg

    @staticmethod
    def create_motor_event_message(
        msg_type: MessageType,
        motor_id: int,
        success: bool,
        event_type: int,
        event_value: float,
        num_in_queue: int,
        executed_with_count: int,
    ) -> Message:
        """
        Creates a MotorEvent message.

        Args:
        msg_type: The MessageType.
        motor_id: The motor identifier (UINT8).
        success: Whether the event was successful (BOOL).
        event_type: The event type (UINT8).
        event_value: The event value (FLOAT).
        num_in_queue: Number of events in the queue (UINT8).
        executed_with_count: Number executed with this event (UINT8).

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.motor_event_proto())
        msg.set_field("motor_id", motor_id)
        msg.set_field("success", success)
        msg.set_field("event_type", event_type)
        msg.set_field("event_value", event_value)
        msg.set_field("num_in_queue", num_in_queue)
        msg.set_field("executed_with_count", executed_with_count)
        return msg

    @staticmethod
    def create_control_go_message(msg_type: MessageType, rand_val: int) -> Message:
        """
        Creates a ControlGo message.

        Args:
        msg_type: The MessageType.
        rand_val: An INT8 random value.

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.control_go_proto())
        msg.set_field("rand", rand_val)
        return msg

    @staticmethod
    def create_control_done_message(
        msg_type: MessageType, success: bool, time_val: int, executed: int
    ) -> Message:
        """
        Creates a ControlDone message.

        Args:
        msg_type: The MessageType.
        success: Whether the operation was successful (BOOL).
        time_val: Execution time (UINT32).
        executed: Number executed (UINT8).

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.control_done_proto())
        msg.set_field("success", success)
        msg.set_field("time", time_val)
        msg.set_field("executed", executed)
        return msg

    @staticmethod
    def create_start_sensor_datastream_message(
        msg_type: MessageType, sensor_id: int, frequency: int
    ) -> Message:
        """
        Creates a StartSensorDatastream message.

        Args:
        msg_type: The MessageType.
        sensor_id: The sensor identifier (UINT8).
        frequency: Frequency in Hz (UINT8).

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.start_sensor_datastream_proto())
        msg.set_field("sensor_id", sensor_id)
        msg.set_field("frequency", frequency)
        return msg

    @staticmethod
    def create_sensor_datastream_message(
        msg_type: MessageType, sensor_id: int, data: float
    ) -> Message:
        """
        Creates a SensorDatastream message.

        Args:
        msg_type: The MessageType.
        sensor_id: The sensor identifier (UINT8).
        data: The sensor data (FLOAT).

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.sensor_datastream_proto())
        msg.set_field("sensor_id", sensor_id)
        msg.set_field("data", data)
        return msg

    @staticmethod
    def create_stop_sensor_datastream_message(
        msg_type: MessageType, sensor_id: int
    ) -> Message:
        """
        Creates a StopSensorDatastream message.

        Args:
        msg_type: The MessageType.
        sensor_id: The sensor identifier (UINT8).

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.stop_sensor_datastream_proto())
        msg.set_field("sensor_id", sensor_id)
        return msg

    @staticmethod
    def create_clear_control_queue_message(msg_type: MessageType, rand_val: int) -> Message:
        """
        Creates a ClearControlQueue message.

        Args:
        msg_type: The MessageType.
        rand_val: An INT8 random value.

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.clear_control_queue_proto())
        msg.set_field("rand", rand_val)
        return msg

    @staticmethod
    def create_error_message(msg_type: MessageType, error_code: int) -> Message:
        """
        Creates an Error message.

        Args:
        msg_type: The MessageType.
        error_code: The error code (UINT8).

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.error_message_proto())
        msg.set_field("error_code", error_code)
        return msg

    @staticmethod
    def create_stop_message(msg_type: MessageType, rand_val: int) -> Message:
        """
        Creates a Stop message.

        Args:
        msg_type: The MessageType.
        rand_val: An INT8 random value.

        Returns:
        A Message object.
        """
        msg = Message.from_type_and_proto(msg_type, MessageDefinitions.stop_proto())
        msg.set_field("rand", rand_val)
        return msg
