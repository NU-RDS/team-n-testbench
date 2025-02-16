"""
gui.py

A python gui to control N-tendon robotic finger
Deals with the GUI and the communication with the teensy, leveraging the rdscom library
"""

import argparse
import sys
from com.mcu_com import MCUCom
from interface.app import AppInterface

# options
# default to COM4 on Windows, or /dev/ttyACM0 on Linux/Mac
DEFAULT_PORT = "COM4" if sys.platform == "win32" else "/dev/ttyACM0"

class ApplicationContext:
    @staticmethod
    def get_instance():
        if not hasattr(ApplicationContext, "instance"):
            # throw an error
            raise Exception("ApplicationContext not initialized")
        return ApplicationContext.instance
    
    def __init__(self, args):
        self.mcu_com = MCUCom(args.port, args.baudrate)
        self.instance = self
        self.app_interface = AppInterface()

    def tick(self):
        self.mcu_com.tick()
        self.app_interface.tick()
        

def main():
    parser = argparse.ArgumentParser(description="N-tendon robotic finger control GUI")
    parser.add_argument("--port", type=str, default=DEFAULT_PORT, help="The serial port to connect to")
    parser.add_argument("--baudrate", type=int, default=115200, help="The baudrate to use")

    args = parser.parse_args()
    app_context = ApplicationContext(args)

    while True:
        app_context.instance.tick()


if __name__ == "__main__":
    main()