from interface.dock import dock, ImmediateInspectorDock
from rdscom.rdscom import (Message, CommunicationChannel, MessageType)
from app_context import ApplicationContext
from interface.imqt import FontStyle, LayoutAlignment
from com.message_definitions import MessageDefinitions
from util.timer import TimerGroup, TimedTask
from PyQt5.QtCore import Qt
from interface.docks.control import ControlModes

@dock("Command Buffer")
class CommandBufferDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ApplicationContext.mcu_com.add_message_event_callback(self.redraw)
        self.timer_group.add_task(20, self.redraw)

    def draw_label(self, label, value):
        self.builder.begin_horizontal()
        self.builder.label(label, font_style=FontStyle.BOLD)
        value_str = str(value)
        self.builder.label(value_str)
        self.builder.end_horizontal()

    def calculate_command_groups(self, commands : Message):
        # group the commands
        command_groups = [] # lists of lists of commands
        current_group = []
        for command in commands:
            is_simultaneous = command.get_field("simultaneous").value()
            # if it is simultaneous, add it to the current group
            if is_simultaneous:
                print("Adding to current group")
                current_group.append(command)
            else:
                if len(current_group) > 0:
                    command_groups.append(current_group)
                    current_group = []
                command_groups.append([command])

        if len(current_group) > 0:
            command_groups.append(current_group)

        return command_groups

    def draw_command_bufer(self):
        commands = ApplicationContext.mcu_com.get_current_command_buffer()
        command_groups = self.calculate_command_groups(commands)
        # draw the groups
        self.builder.begin_scroll()
        for idx, group in enumerate(command_groups):
            group_title = f"Command Group {idx}"
            show = self.builder.begin_foldout_header_group(group_title)
            if show:
                for command in group:
                    self.builder.begin_horizontal()
                    motor_id = command.get_field("motor_id").value()
                    control_mode = command.get_field("control_mode").value()
                    control_value = command.get_field("control_value").value()
                    self.builder.label(f"Motor ID: {motor_id}")
                    self.builder.label(f"Mode: {ControlModes.to_string(control_mode)} ({control_mode})")
                    self.builder.label(f"Value: {control_value}")
                    self.builder.end_horizontal()
            self.builder.end_foldout_header_group()

        self.builder.flexible_space()
        self.builder.end_scroll()

        
    def draw_inspector(self):
        self.builder.start()
        self.builder.begin_scroll(policy=Qt.ScrollBarAlwaysOn)
        self.draw_command_bufer()
        self.builder.flexible_space()
        self.builder.end_scroll()

    def redraw(self):
        self.set_dirty()
        self.show()
        