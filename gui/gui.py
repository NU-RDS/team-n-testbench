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
    mcu_com : MCUCom
    app_interface : AppInterface
    _instance : "ApplicationContext" = None

    @staticmethod
    def get_instance() -> "ApplicationContext":
        if ApplicationContext._instance is None:
            raise Exception("Application context not initialized")
        return ApplicationContext._instance
    
    @staticmethod
    def set_instance(instance : "ApplicationContext"):
        if ApplicationContext._instance is not None:
            raise Exception("Application context already initialized")
        ApplicationContext._instance = instance
    
    def __init__(self, args):
        self.mcu_com = MCUCom(args.port, args.baudrate)
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
    ApplicationContext.set_instance(app_context)


    while True:
        ApplicationContext.get_instance().tick()


if __name__ == "__main__":
    main()