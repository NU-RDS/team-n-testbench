from interface.dock import dock, ImmediateInspectorDock
from interface.imqt import LayoutUtility, FontStyle
from rdscom.rdscom import (Message, CommunicationChannel, DataField)
from com.message_definitions import MessageDefinitions
from app_context import ApplicationContext

@dock("Message Information")
class MessageHistoryDock(ImmediateInspectorDock):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("MessageHistoryDock init")
        self.message_history = []

    def draw_label(self, label, value):
        print(f"{label}: {value}")
        self.builder.begin_horizontal()
        self.builder.label(label, font_style=FontStyle.BOLD)
        value_str = str(value)
        self.builder.label(value_str)
        self.builder.end_horizontal()

    def draw_inspector(self):
        self.builder.start()

        self.builder.begin_scroll()

        protos = MessageDefinitions.all_protos()

        for proto in protos:
            human_readable = MessageDefinitions.get_human_name(proto.identifier())
            show = self.builder.begin_foldout_header_group(f"{human_readable}")
            if show:
                for field_name in proto.field_names():
                    field = proto.find_field(field_name).value()
                    self.builder.begin_vertical(boxed=True)

                    self.draw_label("Field Name", field_name)
                    self.draw_label("Field Type", field.type)
                    self.draw_label("Field Size", DataField.get_size_of_type(field.type))
                    self.draw_label("Field Offset", field.offset)

                    self.builder.end_vertical()
                    self.builder.space(2)

            self.builder.end_foldout_header_group()



        self.builder.end_scroll()

        