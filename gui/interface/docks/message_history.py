from interface.dock import dock, ImmediateInspectorDock
from rdscom.rdscom import (Message, CommunicationChannel, MessageType)
from app_context import ApplicationContext
from interface.imqt import FontStyle, LayoutAlignment
from com.message_definitions import MessageDefinitions
from util.timer import TimerGroup, TimedTask

@dock("Message History")
class MessageHistoryDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ApplicationContext.mcu_com.add_message_event_callback(self.redraw)
        self.timer_group.add_task(2000, self.redraw)

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
            self.builder.label("Meta Data", font_style=FontStyle.BOLD)
            self.builder.begin_horizontal()
            self.builder.label("Message Type", message.type())
            self.builder.label("Message ID", message.message_number())
            self.builder.end_horizontal()

            fields = message.data().type().field_names()
            for field_name in fields:
                value = message.data().get_field(field_name).value()
                self.draw_label(field_name, value)

        self.builder.end_foldout_header_group()
        
    def draw_inspector(self):
        self.builder.start()
        self.builder.begin_scroll()
        message_history = ApplicationContext.mcu_com.get_message_history()
        # draw in reverse order
        for message in reversed(message_history):
            self.draw_message(message)

        # self.builder.flexible_space()
        self.builder.end_scroll()

    def redraw(self):
        self.set_dirty()
        self.show()
        