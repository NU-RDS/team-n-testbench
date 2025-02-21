from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle
from rdscom.rdscom import (Message, CommunicationChannel, DataField)
from com.message_definitions import MessageDefinitions
from app_context import ApplicationContext

@dock("Control Panel")
class ControlDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("MessageHistoryDock init")
        self.message_history = []

    def draw_motor_control(self, motor_num : int):
        self.builder.label(f"Motor {motor_num}", font_style=FontStyle.BOLD)
        self.builder.begin_horizontal()
        self.builder.label("Speed")
        self.builder.slider(f"Speed {motor_num}", min_value=0, max_value=100, initial_value=50)
        self.builder.end_horizontal()

        self.builder.begin_horizontal()
        self.builder.label("Direction")
        # self.builder.checkbox(f"Direction {motor_num}")
        self.builder.end_horizontal()

        self.builder.begin_horizontal()
        self.builder.label("Enable")
        # self.builder.checkbox(f"Enable {motor_num}")
        self.builder.end_horizontal()


    def draw_command_bufer(self):
        self.builder.label("Command Buffer", font_style=FontStyle.BOLD)

    def draw_inspector(self):
        self.builder.start()

        self.builder.begin_horizontal()

        for motor_num in range(2):
            self.builder.begin_vertical()
            self.draw_motor_control(motor_num)
            self.builder.end_vertical()

        self.builder.begin_scroll()
        self.draw_command_bufer()
        self.builder.end_scroll()

        self.builder.end_horizontal()

        