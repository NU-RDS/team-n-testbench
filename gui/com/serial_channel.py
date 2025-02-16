from rdscom.rdscom import (
    CommunicationChannel,
    Message
)

import serial

class PySerialChannel(CommunicationChannel):
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)

    def receive(self) -> bytearray:
        # Read all available bytes.
        data = self.ser.read(self.ser.in_waiting or 1)
        if len(data) > 0:
            print(f"[serial][len({len(data)})] {data.decode('utf8')}")
        return bytearray(data)

    def send(self, message: Message) -> None:
        serialized = message.serialize()
        self.ser.write(serialized)