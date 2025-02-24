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

        self.timer_group.add_task(50000, self.send_hearbeat)

    def handle_message_event(self, message: Message):
        self.message_history.append(message)
        for callback in self.message_event_callbacks:
            callback(message)

    def get_message_history(self) -> list[Message]:
        return self.message_history

    def send_message(self, message: Message, ack_required: bool = False, on_failure = None):
        for callback in self.on_send_callbacks:
            callback(message)

        self.handle_message_event(message)
        self.comm_interface.send_message(message, ack_required, on_failure)

    def send_buffer_message(self, message: Message):
        self.command_buffer.add_command(message)

    def send_buffer(self):
        self.command_buffer.send_command_buffer_async(self.comm_interface)

    def get_buffered_messages(self):
        return self.command_buffer.get_buffer()
    
    def on_heartbeat_failure(self):
        print("Heartbeat failure")
    
    def send_hearbeat(self):
        # print("Sending heartbeat")
        heartbeat = MessageDefinitions.create_heartbeat_message(MessageType.REQUEST, random.randint(0, 100))
        self.send_message(heartbeat, ack_required=True, on_failure=self.on_heartbeat_failure)

    def tick(self):
        self.comm_interface.tick()
        self.timer_group.tick()

        


