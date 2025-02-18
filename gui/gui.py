"""
gui.py

A python gui to control N-tendon robotic finger
Deals with the GUI and the communication with the teensy, leveraging the rdscom library
"""

import argparse
import sys
from app_context import ApplicationContext

# default to COM4 on Windows, or /dev/ttyACM0 on Linux/Mac
DEFAULT_PORT = "COM4" if sys.platform == "win32" else "/dev/ttyACM0"

def main():
    parser = argparse.ArgumentParser(description="N-tendon robotic finger control GUI")
    parser.add_argument(
        "--port", type=str, default=DEFAULT_PORT, help="The serial port to connect to"
    )
    parser.add_argument(
        "--baudrate", type=int, default=115200, help="The baudrate to use"
    )

    args = parser.parse_args()
    ApplicationContext.initialize(args)

    while True:
        ApplicationContext.tick()

if __name__ == "__main__":
    main()
