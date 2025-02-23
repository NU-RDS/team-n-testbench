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
        self.tx_message_buffer = []
        self.on_send_callbacks = []  # listof func(message)
        self.on_receive_callbacks = []  # listof func(message)

        # now add all of the prototypes
        for proto in MessageDefinitions.all_protos():
            self.comm_interface.add_prototype(proto)

        self.timer_group.add_task(100, self.send_hearbeat)

    def add_send_callback(self, callback):
        self.on_send_callbacks.append(callback)

    def add_receive_callback(self, callback):
        self.on_receive_callbacks.append(callback)

        for id in MessageDefinitions.all_proto_ids():
            self.comm_interface.add_callback(id, MessageType.REQUEST, callback)
            self.comm_interface.add_callback(id, MessageType.RESPONSE, callback)
            self.comm_interface.add_callback(id, MessageType.ERROR, callback)

    def send_message(self, message: Message):
        for callback in self.on_send_callbacks:
            callback(message)
        self.comm_interface.send_message(message)

    def send_buffer_message(self, message: Message):
        # print("Buffering message")
        self.tx_message_buffer.append(message)

    def send_buffer(self):
        for message in self.tx_message_buffer:
            self.send_message(message)

        self.tx_message_buffer = []

    def get_buffered_messages(self):
        return self.tx_message_buffer
    
    def send_hearbeat(self):
        print("Sending heartbeat")
        heartbeat = MessageDefinitions.create_heartbeat_message(MessageType.REQUEST, random.randint(0, 100))
        self.send_message(heartbeat)

    def tick(self):
        self.comm_interface.tick()
        self.timer_group.tick()

        


