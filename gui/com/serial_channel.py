from rdscom.rdscom import (
    CommunicationChannel,
    Message
)

import serial

class PySerialChannel(CommunicationChannel):
    def __init__(self, port, baudrate=115200):
        try :
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            self.is_open = True
        except serial.SerialException:
            print("Error: Could not open serial port.")
            self.ser = None
            self.is_open = False

    def receive(self) -> bytearray:
        if not self.is_open:
            # print("Error: Serial port is not open.")
            return bytearray()

        # Read all available bytes.
        data = self.ser.read(self.ser.in_waiting or 1)
        if len(data) > 0:
            print(f"[serial][len({len(data)})] {data.decode('utf8')}")
        return bytearray(data)

    def send(self, message: Message) -> None:
        if not self.is_open:
            print("Error: Serial port is not open.")
            return
        
        serialized = message.serialize()
        self.ser.write(serialized)