from interface.dock import dock, ImmediateInspectorDock
from rdscom.rdscom import (Message, CommunicationChannel, MessageType)
from app_context import ApplicationContext
from interface.imqt import FontStyle, LayoutAlignment
from com.message_definitions import MessageDefinitions
from util.timer import TimerGroup, TimedTask
from PyQt5.QtCore import Qt

@dock("Message History")
class MessageHistoryDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ApplicationContext.mcu_com.add_message_event_callback(self.redraw)
        self.timer_group.add_task(200, self.redraw)

    def draw_label(self, label, value):
        self.builder.begin_horizontal()
        self.builder.label(label, font_style=FontStyle.BOLD)
        value_str = str(value)
        self.builder.label(value_str)
        self.builder.end_horizontal()

    def draw_message(self, message : Message):
        type_str = MessageType.to_string(message.type())
        payload_type_str = MessageDefinitions.get_human_name(message.data().type().identifier())

        show = self.builder.begin_foldout_header_group(f"{payload_type_str} {type_str} - {message.message_number()}", indent=10)
        if show:
            self.builder.begin_vertical()
            self.builder.label("Meta Data", font_style=FontStyle.BOLD)
            self.builder.begin_horizontal(indent=10)
            self.draw_label("Message Type:", type_str)
            self.draw_label("Message ID:", str(message.message_number()))
            self.draw_label("Payload Type:", message.data().type().identifier())
            self.builder.end_horizontal()
            self.builder.end_vertical()

            self.builder.begin_vertical()
            self.builder.label("Payload", font_style=FontStyle.BOLD)
            self.builder.begin_vertical(indent=10)
            fields = message.data().type().field_names()
            for field_name in fields:
                value = message.data().get_field(field_name).value()
                self.draw_label(field_name, value)
            self.builder.end_vertical()
            self.builder.end_vertical()

        self.builder.end_foldout_header_group()
        
    def draw_inspector(self):
        self.builder.start()
        self.builder.begin_scroll(policy=Qt.ScrollBarAlwaysOn)
        message_history = ApplicationContext.mcu_com.get_message_history()
        # draw in reverse order
        max_messages = min(20, len(message_history))
        for message in reversed(message_history[-max_messages:]):
            self.draw_message(message)

        self.builder.flexible_space()
        self.builder.end_scroll()

    def redraw(self):
        self.set_dirty()
        self.show()
        