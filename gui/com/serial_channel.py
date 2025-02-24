from rdscom.rdscom import (
    CommunicationChannel,
    Message
)

import serial
import threading

class PySerialChannel(CommunicationChannel):
    def __init__(self, port, baudrate=115200):
        self.history = ""
        self.rx_callbacks = []
        self.tx_callbacks = []
        self._write_lock = threading.Lock()
        self._read_lock = threading.Lock()
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
        
        # self._read_lock.acquire()
        # Read all available bytes.
        data = self.ser.read(self.ser.in_waiting or 1)
        if len(data) > 0:
            print(f"[recieved:{len(data)}] {data.decode('utf8')}")
            # append the data to the history as a string
            self.history += data.decode('utf8') + "\n"
            for callback in self.rx_callbacks:
                callback(data)

        # self._read_lock.release()

        return bytearray(data)

    def send(self, message: Message) -> None:
        if not self.is_open:
            print("Error: Serial port is not open.")
            return
        
        # self._write_lock.acquire()

        self.history += message.serialize().decode('utf8') + "\n"
        decode_message = message.serialize().decode('utf8')
        print(f"[sent:{len(decode_message)}] {message.serialize().decode('utf8')}")

        for callback in self.tx_callbacks:
            callback(message.serialize().decode('utf8'))
        serialized = message.serialize()
        self.ser.write(serialized)

        # self._write_lock.release()

    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history = ""

    def add_receive_callback(self, callback):
        self.rx_callbacks.append(callback)

    def add_transmit_callback(self, callback):
        self.tx_callbacks.append(callback)