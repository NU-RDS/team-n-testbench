from interface.dock import dock, ImmediateInspectorDock
from rdscom.rdscom import (Message, CommunicationChannel)
from app_context import ApplicationContext

@dock("Message History")
class MessageHistoryDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        ApplicationContext.mcu_com.add_receive_callback(self.update_message_history)
        self.message_history = []

    def draw_inspector(self):
        self.builder.start()

        self.builder.begin_vertical()

        for message in self.message_history:
            self.builder.label(f"Message ID: {message.id}", text_color="black", bg_color="lightgray", font_size=14)
            self.builder.label(f"Message Type: {message.type}", text_color="black", bg_color="lightgray", font_size=14)
            self.builder.label(f"Message Data: {message.data}", text_color="black", bg_color="lightgray", font_size=14)
            self.builder.label(f"Message Timestamp: {message.timestamp}", text_color="black", bg_color="lightgray", font_size=14)


        self.builder.end_vertical()


    def update_message_history(self, message : Message):
        self.message_history.append(message)
        