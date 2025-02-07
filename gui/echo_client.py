"""
echo_client.py

A simple Python client that sends a message over a serial port using rdscom,
and prints the echoed reply from an Arduino running the echo server.
"""

import sys
import time
import serial
from rdscom import (
    CommunicationInterface,
    CommunicationInterfaceOptions,
    DataPrototype,
    DataFieldType,
    Message,
    MessageType,
    check,
    default_error_callback,
    CommunicationChannel
)

# ---------------------------------------------------------
# PySerialChannel: A CommunicationChannel implementation using PySerial.
# ---------------------------------------------------------
class PySerialChannel(CommunicationChannel):
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
    
    def receive(self) -> bytearray:
        # Read all available bytes.
        data = self.ser.read(self.ser.in_waiting or 1)
        return bytearray(data)
    
    def send(self, message: Message) -> None:
        serialized = message.serialize()
        self.ser.write(serialized)

# ---------------------------------------------------------
# Callback to print any received (echoed) message.
# ---------------------------------------------------------
def on_echo_message(message: Message) -> None:
    print("Echo received:")
    message.print_clean(sys.stdout)

def main():
    # Replace this port with your actual serial port (e.g., "COM3" on Windows or "/dev/ttyACM0" on Linux/Mac)
    port = "/dev/ttyACM0" if len(sys.args) < 2 else sys.args[1]

    try:
        channel = PySerialChannel(port)
    except serial.SerialException as e:
        sys.stderr.write(f"Failed to open serial port {port}: {e}\n")
        sys.exit(1)

    # Use a simple time function (milliseconds since epoch).
    options = CommunicationInterfaceOptions(time_function=lambda: int(time.time() * 1000))
    com = CommunicationInterface(channel, options)

    # Define the same echo prototype as on the Arduino (identifier 1 with a UINT8 "dummy" field).
    echoProto = DataPrototype(1)
    echoProto.add_field("dummy", DataFieldType.UINT8)
    com.add_prototype(echoProto)

    # Register callbacks to print any echoed messages.
    com.add_callback(1, MessageType.REQUEST, on_echo_message)
    com.add_callback(1, MessageType.RESPONSE, on_echo_message)
    com.add_callback(1, MessageType.ERROR, on_echo_message)

    # Build a message using the echo prototype.
    msg = Message.from_type_and_proto(MessageType.REQUEST, echoProto)
    res = msg.set_field("dummy", 42)
    if check(default_error_callback(sys.stderr), res):
        sys.exit(1)
    
    # Send the message over serial.
    com.send_message(msg, ack_required=False)
    print("Message sent over serial. Waiting for echo...")

    # Main loop: periodically call tick() so that incoming messages are processed.
    try:
        while True:
            com.tick()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting serial client.")
        sys.exit(0)

if __name__ == "__main__":
    main()
