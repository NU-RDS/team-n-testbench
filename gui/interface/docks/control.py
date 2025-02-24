from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle, LayoutAlignment
from rdscom.rdscom import Message, CommunicationChannel, DataField
from com.message_definitions import MessageDefinitions
from com.mcu_com import MCUCom
from app_context import ApplicationContext
from rdscom.rdscom import MessageType
from interface.telemetry import Telemetry


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

class ControlValues:
    def __init__(self, control_value : int, simultaneous : bool):
        self.control_value = control_value
        self.simultaneous = simultaneous


@dock("Control Panel")
class ControlDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)

    def send_control_command(
        self, motor_num: int, control_mode: ControlModes, control_value: int, simultaneous: bool
    ):
        message = MessageDefinitions.create_motor_control_message(
            MessageType.REQUEST, motor_num, control_mode, control_value, simultaneous
        )

        ApplicationContext.mcu_com.send_buffer_message(message)

    def send_datastream_start(self, joint_number: int):
        ApplicationContext.telemetry.enable_sensor_datastream(joint_number, 10)

    def send_datastream_stop(self, joint_number: int):
        ApplicationContext.telemetry.disable_sensor_datastream(joint_number)
        

    def send_datastream_stop(self, joint_number: int):
        message = MessageDefinitions.create_stop_sensor_datastream_message(MessageType.REQUEST, joint_number)
        ApplicationContext.mcu_com.send_message(message, ack_required=True)


    def draw_control_value(self, type : str, label: str, default_value: int) -> ControlValues:
        self.builder.label(label, font_style=FontStyle.BOLD)
        value = self.builder.slider(type, default_value, min_value=-100, max_value=100)
        simultaneous = self.builder.toggle("Simultaneous", initial_value=False)
        return ControlValues(value, simultaneous)
        
    def draw_joint_control(self, joint_number: int):
        self.builder.label(f"Joint {joint_number}", font_style=FontStyle.BOLD)

        self.builder.begin_vertical()
        mode = self.builder.dropdown(
            "Control Mode", options=ControlModes.all_modes_str(), initial_value=0
        )

        mode_str = ControlModes.to_string(mode)
        control_values = self.draw_control_value("Control Value", f"{mode_str} Value", 0)

        # button to submit control
        if self.builder.button("Submit Control"):
            control_mode = ControlModes.all_modes()[mode]
            self.send_control_command(joint_number, control_mode, control_values.control_value, control_values.simultaneous)

        data_stream =  self.builder.toggle("Enable Datastream", initial_value=False)
        if data_stream and not ApplicationContext.telemetry.is_active(joint_number):
            self.send_datastream_start(joint_number)
        elif not data_stream and ApplicationContext.telemetry.is_active(joint_number):
            self.send_datastream_stop(joint_number)

        self.builder.end_vertical()

    def draw_command_creator(self):
        self.builder.begin_horizontal()
        for motor_num in range(2):
            self.builder.begin_vertical(alignment=LayoutAlignment.CENTER)
            self.draw_joint_control(motor_num)
            self.builder.end_vertical()
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

    def draw_inspector(self):
        self.builder.start()
        self.draw_command_creator()

        if self.builder.button("Send Command Buffer"):
            # add an execute command)
            ApplicationContext.mcu_com.send_buffer()
            self.set_dirty()
            self.show()
        self.builder.end_vertical()

