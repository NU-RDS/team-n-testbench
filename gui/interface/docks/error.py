from interface.dock import dock, ImmediateInspectorDock
from app_context import ApplicationContext
from interface.imqt import FontStyle, LayoutAlignment
from interface.error_manager import ErrorManager, ErrorSeverity, Error
from app_context import ApplicationContext
from PyQt5.QtCore import Qt

@dock("Errors")
class MessageHistoryDock(ImmediateInspectorDock):
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

    def get_error_color(self, error_severity : ErrorSeverity):
        match error_severity:
            case ErrorSeverity.INFO:
                return "blue"
            case ErrorSeverity.WARNING:
                return "yellow"
            case ErrorSeverity.ERROR:
                return "red"
            case _:
                return "black"

    def draw_error(self, error : Error):
        color = self.get_error_color(error.severity)
        self.builder.begin_horizontal()
        self.builder.label(error.message, font_style=FontStyle.BOLD, text_color=color)
        self.builder.end_horizontal()
        
    def draw_inspector(self):
        if ApplicationContext.error_manager is None:
            return

        self.builder.start()
        self.builder.begin_scroll(policy=Qt.ScrollBarAlwaysOn)
        for error in ApplicationContext.error_manager.get_errors():
            self.draw_error(error)

        self.builder.flexible_space()
        self.builder.end_scroll()


    def redraw(self):
        self.set_dirty()
        self.show()
        