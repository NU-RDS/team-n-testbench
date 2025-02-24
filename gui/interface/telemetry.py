from rdscom.rdscom import Message, CommunicationChannel, DataField, CommunicationInterface, MessageType
from com.message_definitions import MessageDefinitions
from interface.error_manager import ErrorSeverity
from app_context import ApplicationContext

class SensorDatastream:
    def __init__(self, joint_number: int, frequency: float):
        self.joint_number = joint_number
        self.frequency = frequency

class Telemetry:
    def __init__(self):
        self.sensor_datastreams : list[SensorDatastream] = []

    def enable_sensor_datastream(self, joint_number: int, frequency: float):
        datastream = SensorDatastream(joint_number, frequency)
        self.sensor_datastreams.append(datastream)
        
        enable_message = MessageDefinitions.create_start_sensor_datastream_message(MessageType.REQUEST, joint_number, frequency)
        ApplicationContext.mcu_com.send_message(enable_message, ack_required=True, on_failure=self._on_enable_failure)

    def _on_enable_failure(self, message: Message):
        joint_number = message.data().get_field("joint_number").value()
        ApplicationContext.error_manager.report_error(f"Failed to enable sensor datastream for joint {joint_number}", ErrorSeverity.WARNING)

    def disable_sensor_datastream(self, joint_number: int):
        in_list = [datastream for datastream in self.sensor_datastreams if datastream.joint_number == joint_number]
        if len(in_list) == 0:
            ApplicationContext.error_manager.report_error(f"No datastream for joint number {joint_number}", ErrorSeverity.WARNING)
            return
        
        datastream = in_list[0]
        disable_message = MessageDefinitions.create_stop_sensor_datastream_message(MessageType.REQUEST, joint_number)
        ApplicationContext.mcu_com.send_message(disable_message, ack_required=True, on_failure=self._on_disable_failure)

    def _on_disable_failure(self, message: Message):
        joint_number = message.data().get_field("joint_number").value()
        ApplicationContext.error_manager.report_error(f"Failed to disable sensor datastream for joint {joint_number}", ErrorSeverity.WARNING)

    def is_active(self, joint_number: int) -> bool:
        in_list = [datastream for datastream in self.sensor_datastreams if datastream.joint_number == joint_number]
        return len(in_list) > 0

