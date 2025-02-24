from rdscom.rdscom import (
    CommunicationChannel,
    Message
)

import serial
import threading

class PySerialChannel(CommunicationChannel):
    def __init__(self, port, baudrate=115200):
        self.history = b""
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
            return bytearray()
            
        # Acquire and immediately release the lock using a context manager.
        with self._read_lock:
            data = self.ser.read(self.ser.in_waiting or 1)
        
        # Now, outside of the lock, process the data.
        if data:
            print(f"[received:{len(data)}] {data}")
            self.history += data + b"\n"
            for callback in self.rx_callbacks:
                # Calling callbacks outside the lock prevents blocking other threads.
                callback(data)
                
        return bytearray(data)


    def send(self, message: Message) -> None:
        if not self.is_open:
            print("Error: Serial port is not open.")
            return

        # Acquire the write lock using a context manager.
        with self._write_lock:
            serialized = message.serialize()
            self.history += serialized + b"\n"
            print(f"[sent:{len(serialized)}] {serialized}")
            for callback in self.tx_callbacks:
                callback(decoded_message)
            self.ser.write(serialized)


    def get_history(self):
        # decode the bytes to a string
        try:
            return self.history.decode('utf8')
        except UnicodeDecodeError:
            # just do a normal decode
            return self.history
    
    def clear_history(self):
        self.history = ""

    def add_receive_callback(self, callback):
        self.rx_callbacks.append(callback)

    def add_transmit_callback(self, callback):
        self.tx_callbacks.append(callback)