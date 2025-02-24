import enum

class ErrorSeverity(enum.Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    STOP_EXECUTION = 4

class Error:
    def __init__(self, message: str, severity: ErrorSeverity):
        self.message = message
        self.severity = severity

    def __str__(self):
        return f"{self.severity.name}: {self.message}"

    def __repr__(self):
        return self.__str__()

class ErrorManager:
    def __init__(self):
        self.errors = []

    def get_errors(self) -> list[Error]:
        return self.errors

    def report_error(self, message: str, severity: ErrorSeverity):
        error = Error(message, severity)
        self.errors.append(error)
        print(error)