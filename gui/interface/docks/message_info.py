from interface.dock import dock, ImmediateInspectorDock
from rdscom.rdscom import (Message, CommunicationChannel, DataField)
from com.message_definitions import MessageDefinitions
from app_context import ApplicationContext

@dock("Message Information")
class MessageHistoryDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("MessageHistoryDock init")
        self.message_history = []

    def draw_inspector(self):
        self.builder.start()

        self.builder.begin_scroll()

        protos = MessageDefinitions.all_protos()

        for proto in protos:
            human_readable = MessageDefinitions.get_human_name(proto.identifier())
            self.builder.begin_toggle_group(f"{human_readable}")
            for field_name in proto.field_names():
                field = proto.find_field(field_name).value()
                self.builder.label(f"Field: {field_name}")
                self.builder.label(f"Type: {field.type}")
                self.builder.label(f"Size: {DataField.get_size_of_type(field.type)}")
                self.builder.label(f"Offset: {field.offset}")

            self.builder.end_toggle_group()



        self.builder.end_scroll()

        