"""
echo_client.py

A simple Python client that sends a message over a serial port using rdscom,
and prints the echoed reply from an Arduino running the echo server.
"""

import sys
import time
import serial
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

# default to COM4 on Windows, or /dev/ttyACM0 on Linux/Mac
DEFAULT_PORT = "COM4" if sys.platform == "win32" else "/dev/ttyACM0"

g_com: CommunicationInterface = None


# ---------------------------------------------------------
# PySerialChannel: A CommunicationChannel implementation using PySerial.
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Callback to print any received (echoed) message.
# ---------------------------------------------------------
def on_echo_message(message: Message) -> None:
    print("Echo received:")
    message.print_clean(sys.stdout)
    response = Message.create_response(message, message.data())
    g_com.send_message(response, ack_required=False)

def main():
    # Replace this port with your actual serial port (e.g., "COM3" on Windows or "/dev/ttyACM0" on Linux/Mac)
    port = DEFAULT_PORT if len(sys.argv) < 2 else sys.argv[1]

    try:
        channel = PySerialChannel(port)
    except serial.SerialException as e:
        sys.stderr.write(f"Failed to open serial port {port}: {e}\n")
        sys.exit(1)

    # Use a simple time function (milliseconds since epoch).
    options = CommunicationInterfaceOptions(
        time_function=lambda: int(time.time() * 1000)
    )
    g_com = CommunicationInterface(channel, options)

    # Define the same echo prototype as on the Arduino (identifier 1 with a UINT8 "dummy" field).
    echoProto = DataPrototype(1)
    echoProto.add_field("dummy", DataFieldType.UINT8)
    g_com.add_prototype(echoProto)

    # Register callbacks to print any echoed messages.
    g_com.add_callback(1, MessageType.REQUEST, on_echo_message)
    g_com.add_callback(1, MessageType.RESPONSE, on_echo_message)
    g_com.add_callback(1, MessageType.ERROR, on_echo_message)

    # Build a message using the echo prototype.
    msg = Message.from_type_and_proto(MessageType.REQUEST, echoProto)
    res = msg.set_field("dummy", 42)
    if Result.check(default_error_callback(sys.stderr), res):
        sys.exit(1)

    # Send the message over serial.
    g_com.send_message(msg, ack_required=False)
    print("Message sent over serial. Waiting for echo...")

    # Main loop: periodically call tick() so that incoming messages are processed.
    try:
        while True:
            g_com.tick()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting serial client.")
        sys.exit(0)


if __name__ == "__main__":
    main()
