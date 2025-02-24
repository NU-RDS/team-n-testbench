from rdscom.rdscom import Message, CommunicationChannel, DataField, CommunicationInterface, MessageType
from com.message_definitions import MessageDefinitions
from interface.error_manager import ErrorSeverity
from app_context import ApplicationContext
from com.mcu_com import MCUCom
import time

class SensorDataSnapshot:
    def __init__(self, timestamp : int, motor_pos : float, motor_vel : float, motor_temp : float, joint_angle : float):
        self.timestamp = timestamp
        self.motor_pos = motor_pos
        self.motor_vel = motor_vel
        self.motor_temp = motor_temp
        self.joint_angle = joint_angle

class SensorDatastream:
    def __init__(self, joint_number: int, frequency: float):
        self.joint_number = joint_number
        self.frequency = frequency
        self.snapshots : list[SensorDataSnapshot] = []

    def add_snapshot(self, snapshot: SensorDataSnapshot):
        # treat this as a circular buffer
        self.snapshots.append(snapshot)
        if len(self.snapshots) > 100:
            # only store the last 50
            self.snapshots = self.snapshots[-50:]

class Telemetry:
    def __init__(self):
        self.sensor_datastreams : list[SensorDatastream] = []

        ApplicationContext.mcu_com.comm_interface.add_callback(MessageDefinitions.sensor_datastream_id(), MessageType.REQUEST, self._on_sensor_datastream)

    def enable_sensor_datastream(self, joint_number: int, frequency: float):
        datastream = SensorDatastream(joint_number, frequency)
        self.sensor_datastreams.append(datastream)
        
        enable_message = MessageDefinitions.create_start_sensor_datastream_message(MessageType.REQUEST, joint_number, frequency)
        ApplicationContext.mcu_com.send_message(enable_message, ack_required=True, on_failure=self._on_enable_failure)

    def _on_enable_failure(self, message: Message):
        joint_number = message.data().get_field("joint_id").value()
        ApplicationContext.error_manager.report_error(f"Failed to enable sensor datastream for joint {joint_number}", ErrorSeverity.WARNING)

    def disable_sensor_datastream(self, joint_number: int):
        in_list = [datastream for datastream in self.sensor_datastreams if datastream.joint_number == joint_number]
        if len(in_list) == 0:
            ApplicationContext.error_manager.report_error(f"No datastream for joint number {joint_number}", ErrorSeverity.WARNING)
            return
        
        datastream = in_list[0]
        disable_message = MessageDefinitions.create_stop_sensor_datastream_message(MessageType.REQUEST, joint_number)
        ApplicationContext.mcu_com.send_message(disable_message, ack_required=True, on_failure=self._on_disable_failure)

        self.sensor_datastreams = [datastream for datastream in self.sensor_datastreams if datastream.joint_number != joint_number]

    def _on_disable_failure(self, message: Message):
        joint_number = message.data().get_field("joint_id").value()
        ApplicationContext.error_manager.report_error(f"Failed to disable sensor datastream for joint {joint_number}", ErrorSeverity.WARNING)

    def is_active(self, joint_number: int) -> bool:
        in_list = [datastream for datastream in self.sensor_datastreams if datastream.joint_number == joint_number]
        return len(in_list) > 0
    
    def _on_sensor_datastream(self, message: Message):
        joint_number = message.data().get_field("joint_id").value()

        in_list = [datastream for datastream in self.sensor_datastreams if datastream.joint_number == joint_number]
        if len(in_list) == 0:
            ApplicationContext.error_manager.report_error(f"Received sensor datastream for unregistered joint {joint_number}", ErrorSeverity.WARNING)
            return
        
        datastream = in_list[0]
        datastream.add_snapshot(SensorDataSnapshot(
            time.time(),
            message.data().get_field("motor_pos").value(),
            message.data().get_field("motor_vel").value(),
            message.data().get_field("motor_temp").value(),
            message.data().get_field("joint_angle").value()
        ))

    def get_datastream(self, joint_number: int) -> SensorDatastream:
        in_list = [datastream for datastream in self.sensor_datastreams if datastream.joint_number == joint_number]
        if len(in_list) == 0:
            return None
        return in_list[0]

