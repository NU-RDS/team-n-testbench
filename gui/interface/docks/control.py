from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle, LayoutAlignment
from rdscom.rdscom import Message, CommunicationChannel, DataField
from com.message_definitions import MessageDefinitions
from com.mcu_com import MCUCom
from app_context import ApplicationContext
from rdscom.rdscom import MessageType


class ControlModes:
    POSITION = 0
    VELOCITY = 1
    TORQUE = 2

    @staticmethod
    def to_string(mode):
        if mode == ControlModes.POSITION:
            return "Position"
        elif mode == ControlModes.VELOCITY:
            return "Velocity"
        elif mode == ControlModes.TORQUE:
            return "Torque"
        else:
            return "Invalid"

    @staticmethod
    def all_modes():
        return [ControlModes.POSITION, ControlModes.VELOCITY, ControlModes.TORQUE]

    @staticmethod
    def all_modes_str():
        return [ControlModes.to_string(mode) for mode in ControlModes.all_modes()]


@dock("Control Panel")
class ControlDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)

    def send_control_command(
        self, motor_num: int, control_mode: ControlModes, control_value: int
    ):
        message = MessageDefinitions.create_motor_control_message(
            MessageType.REQUEST, motor_num, control_mode, control_value, False
        )

        ApplicationContext.mcu_com.send_buffer_message(message)

    def draw_position_control(self):
        self.builder.label("Position Control", font_style=FontStyle.BOLD)
        self.builder.begin_horizontal()
        value = self.builder.slider("Position", min_value=0, max_value=100, initial_value=50)
        self.builder.end_horizontal()
        
        return value

    def draw_velocity_control(self):
        self.builder.label("Velocity Control", font_style=FontStyle.BOLD)
        self.builder.begin_horizontal()
        value = self.builder.slider("Velocity", min_value=0, max_value=100, initial_value=50)
        self.builder.end_horizontal()

        return value

    def draw_torque_control(self):
        self.builder.label("Torque Control", font_style=FontStyle.BOLD)
        self.builder.begin_horizontal()
        value = self.builder.slider("Torque", min_value=0, max_value=100, initial_value=50)
        self.builder.end_horizontal()
        
        return value

    def draw_motor_control(self, motor_num: int):
        self.builder.label(f"Motor {motor_num}", font_style=FontStyle.BOLD)

        self.builder.begin_vertical()
        mode = self.builder.dropdown(
            "Control Mode", options=ControlModes.all_modes_str(), initial_value=0
        )

        control_value = 0
        match mode:
            case ControlModes.POSITION:
                control_value = self.draw_position_control()
            case ControlModes.VELOCITY:
                control_value = self.draw_velocity_control()
            case ControlModes.TORQUE:
                control_value = self.draw_torque_control()
            case _:
                self.builder.label("Invalid Control Mode", font_style=FontStyle.BOLD)

        # button to submit control
        if self.builder.button("Submit Control"):
            control_mode = ControlModes.all_modes()[mode]
            self.send_control_command(motor_num, control_mode, control_value)

        self.builder.end_vertical()

    def draw_command_creator(self):
        self.builder.begin_horizontal()
        for motor_num in range(2):
            self.builder.begin_vertical(boxed=True, alignment=LayoutAlignment.CENTER)
            self.draw_motor_control(motor_num)
            self.builder.end_vertical()
        self.builder.end_horizontal()

    def draw_command_bufer(self):
        self.builder.label("Command Buffer", font_style=FontStyle.BOLD)

        command_groups = [] # lists of lists of commands
        current_group = []
        for command in ApplicationContext.mcu_com.get_buffered_messages():
            is_simultaneous = command.get_field("simultaneous").value()
            if not is_simultaneous:
                if len(current_group) > 0:
                    command_groups.append(current_group)
                    current_group = []
            
            current_group.append(command)

        if len(current_group) > 0:
            command_groups.append(current_group)

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



        self.builder.begin_vertical()
        if self.builder.button("Send Command"):
            ApplicationContext.mcu_com.send_buffer()
        self.builder.end_vertical()

    def draw_inspector(self):
        self.builder.start()

        self.builder.begin_horizontal()

        self.draw_command_creator()

        self.builder.begin_vertical(boxed=True)
        self.builder.begin_scroll()
        self.draw_command_bufer()
        self.builder.end_scroll()
        self.builder.end_vertical()

        self.builder.end_horizontal()
