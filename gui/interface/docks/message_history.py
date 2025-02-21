from interface.dock import dock, ImmediateInspectorDock
from rdscom.rdscom import (Message, CommunicationChannel)
from app_context import ApplicationContext
from interface.imqt import FontStyle, LayoutAlignment

@dock("Message History")
class MessageHistoryDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        ApplicationContext.mcu_com.add_receive_callback(self.update_message_history)
        ApplicationContext.mcu_com.add_send_callback(self.update_message_history)
        self.message_history = []

    def draw_label(self, label, value):
        self.builder.begin_horizontal()
        self.builder.label(label, font_style=FontStyle.BOLD)
        value_str = str(value)
        self.builder.label(value_str)
        self.builder.end_horizontal()

    def draw_message(self, message : Message):
        show = self.builder.begin_foldout_header_group(f"Message {message.message_number()}")
        if show:
            self.builder.begin_vertical(boxed=True, alignment=LayoutAlignment.LEFT)
            self.builder.label("Meta Data", font_style=FontStyle.BOLD)
            self.builder.begin_horizontal()
            self.builder.label("Message Type", message.message_type())
            self.builder.label("Message ID", message.message_id())
            self.builder.label("Message Number", message.message_number())
            self.builder.end_horizontal()

            fields = message.data().type().field_names()
            for field_name in fields:
                self.builder.begin_vertical(boxed=True)
                value = message.data().find_field(field_name).value()
                self.draw_label(field_name, value)
                self.builder.end_vertical()

            self.builder.end_vertical()

        self.builder.end_foldout_header_group()
        


    def draw_inspector(self):
        self.builder.start()

        self.builder.begin_vertical()

        for message in self.message_history:
            self.draw_message(message)

        self.builder.end_vertical()


    def update_message_history(self, message : Message):
        self.message_history.append(message)
        