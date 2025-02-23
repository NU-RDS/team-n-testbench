from rdscom.rdscom import (
    CommunicationChannel,
    Message
)

import serial

class PySerialChannel(CommunicationChannel):
    def __init__(self, port, baudrate=115200):
        self.history = ""
        self.rx_callbacks = []
        self.tx_callbacks = []
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

            # append the data to the history as a string
            self.history += data.decode('utf8')
            for callback in self.rx_callbacks:
                callback(data)
        return bytearray(data)

    def send(self, message: Message) -> None:
        if not self.is_open:
            print("Error: Serial port is not open.")
            return
        
        self.history += message.serialize().decode('utf8')
        for callback in self.tx_callbacks:
            callback(message.serialize().decode('utf8'))
        serialized = message.serialize()
        self.ser.write(serialized)

    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history = ""

    def add_receive_callback(self, callback):
        self.rx_callbacks.append(callback)

    def add_transmit_callback(self, callback):
        self.tx_callbacks.append(callback)