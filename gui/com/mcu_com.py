from rdscom.rdscom import (
    CommunicationInterface,
    CommunicationInterfaceOptions,
    DataPrototype,
    DataFieldType,
    Message,
    MessageType,
    Result,
    default_error_callback,
    CommunicationChannel,
)
from util.timer import TimerGroup, TimedTask
from com.message_definitions import MessageDefinitions
from com.serial_channel import PySerialChannel
from com.command_buffer import CommandBuffer
from interface.error_manager import ErrorSeverity
from app_context import ApplicationContext
import time
import random
import sys

class MCUCom:
    def __init__(self, port: str, baudrate: int = 115200):
        self.channel = PySerialChannel(port, baudrate)
        self.comm_options = CommunicationInterfaceOptions(
            max_retries=3,
            retry_timeout=1000,
            time_function=lambda: int(time.time() * 1000),
        )
        self.comm_interface = CommunicationInterface(
            options=self.comm_options, channel=self.channel
        )
        self.timer_group = TimerGroup()
        self.on_send_callbacks = []  # listof func(message)
        self.command_buffer = CommandBuffer()
        self.message_history = []
        self.message_event_callbacks = []  # listof func(message)

        # now add all of the prototypes
        for proto in MessageDefinitions.all_protos():
            self.comm_interface.add_prototype(proto)

        for proto_id in MessageDefinitions.all_proto_ids():
            self.comm_interface.add_callback(proto_id, MessageType.RESPONSE, self.handle_message_event)
            self.comm_interface.add_callback(proto_id, MessageType.REQUEST, self.handle_message_event)
            self.comm_interface.add_callback(proto_id, MessageType.ERROR, self.handle_message_event)

        self.command_buffer.add_callback_on_send(self.handle_message_event)

        self.timer_group.add_task(10000, self.send_hearbeat)

    def handle_message_event(self, message: Message):
        self.message_history.append(message)
        for callback in self.message_event_callbacks:
            callback(message)

    def get_message_history(self) -> list[Message]:
        return self.message_history

    def send_message(self, message: Message, ack_required: bool = False, on_failure = None, on_success = None):
        for callback in self.on_send_callbacks:
            callback(message)

        self.handle_message_event(message)
        self.comm_interface.send_message(message, ack_required, on_failure, on_success)

    def send_buffer_message(self, message: Message):
        self.command_buffer.add_command(message)

    def send_buffer(self):
        self.command_buffer.send_command_buffer_async(self.comm_interface)

    def get_buffered_messages(self):
        return self.command_buffer.get_buffer()
    
    def get_current_command_buffer(self):
        return self.command_buffer.get_buffer()
    
    def load_command_buffer(self, path : str):
        self.command_buffer.load_buffer_from_file(path)
    
    
    def send_hearbeat(self):
        heartbeat = MessageDefinitions.create_heartbeat_message(MessageType.REQUEST, random.randint(0, 100))
        on_success = lambda response_message : self._heartbeat_msg_on_success(heartbeat, response_message)
        on_failure = lambda : self._on_heartbeat_failure(heartbeat)
        self.send_message(heartbeat, ack_required=True, on_failure=on_failure, on_success=on_success)

    def _on_heartbeat_failure(self, message: Message):
        ApplicationContext.error_manager.report_error(f"Failed to send heartbeat message {message.message_number()}, no response", ErrorSeverity.WARNING)

    def _heartbeat_msg_on_success(self, request_message : Message, response_message : Message):
        # check that the response is a heartbeat
        if response_message.data().type().identifier() != MessageDefinitions.heartbeat_id():
            ApplicationContext.error_manager.report_error("Response message is not a heartbeat message", ErrorSeverity.WARNING)
            return
        
        # check that the message number is the same
        if response_message.message_number() != request_message.message_number():
            ApplicationContext.error_manager.report_error("Response message has different message number", ErrorSeverity.WARNING)

        # check that the random value is the same
        request_random_value = request_message.data().get_field("random_value").value()
        response_random_value = response_message.data().get_field("random_value").value()

        if request_random_value != response_random_value:
            ApplicationContext.error_manager.report_error("Response message has different random value", ErrorSeverity.WARNING)

    def zero(self):
        zero_message = MessageDefinitions.create_zero_command_message(MessageType.REQUEST, 0)
        on_success = lambda response_message : self._on_zero_success(response_message)
        on_failure = lambda : self._on_zero_failure()
        self.send_message(zero_message, ack_required=True, on_failure=on_failure, on_success=on_success)

    def _on_zero_success(self, response_message : Message):
        if response_message.data().type().identifier() != MessageDefinitions.zero_done_id():
            ApplicationContext.error_manager.report_error("Response message is not a zero done message", ErrorSeverity.WARNING)
            return
        
        success = response_message.data().get_field("success").value()
        if success == 0:
            ApplicationContext.error_manager.report_error("Zero failed", ErrorSeverity.WARNING)
        else:
            ApplicationContext.error_manager.report_error("Zero succeeded", ErrorSeverity.INFO)

    def _on_zero_failure(self):
        ApplicationContext.error_manager.report_error("Failed to send zero message", ErrorSeverity.WARNING)


    def tick(self):
        # hack to avoid race condition
        if self.command_buffer.is_sending_buffer() == False:
            self.comm_interface.tick()
        # else:
            # print("Not ticking because buffer is sending")
        self.timer_group.tick()

        


