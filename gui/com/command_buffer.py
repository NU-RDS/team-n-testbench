from rdscom.rdscom import CommunicationChannel, Message, MessageType, CommunicationInterface
from com.message_definitions import MessageDefinitions
from interface.error_manager import ErrorManager, ErrorSeverity
import threading
from app_context import ApplicationContext

class CommandBuffer:
    def __init__(self):
        self.buffer : list[Message] = []
        self._successfully_sent = False
        self._is_waiting = False
        self._is_sending_buffer = False
        self.callbacks_on_send = []

    def add_command(self, message: Message):
        self.buffer.append(message)

    def is_sending_buffer(self):
        return self._is_sending_buffer
    
    def add_callback_on_send(self, callback):
        self.callbacks_on_send.append(callback)
    
    def get_buffer(self):
        # return a copy of the buffer
        return self.buffer.copy()
    
    def clear_buffer(self, channel : CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot clear buffer while sending buffer", ErrorSeverity.WARNING)
            return

        # send a request to clear the buffer
        clear_buffer_message = MessageDefinitions.create_clear_buffer_message()
        on_success = lambda response_message : self._clear_buffer_on_success(clear_buffer_message, response_message)
        on_failure = lambda : self._clear_buffer_on_failure(clear_buffer_message)
        
        channel.send_message(clear_buffer_message, ack_required=True, on_success=on_success, on_failure=on_failure)

        for callback in self.callbacks_on_send:
            callback(clear_buffer_message)

    def _clear_buffer_on_success(self, request_message : Message, response_message : Message):        
        if response_message.data().type().identifier() != MessageDefinitions.CLEAR_BUFFER_MESSAGE:
            ApplicationContext.error_manager.report_error("Response message is not a clear buffer message", ErrorSeverity.WARNING)
            return
        
        self.buffer = []

    def _clear_buffer_on_failure(self, request_message : Message):
        ApplicationContext.error_manager.report_error("Failed to clear buffer message, no response", ErrorSeverity.WARNING)

    def execute_buffer(self, channel: CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot execute buffer while sending buffer", ErrorSeverity.WARNING)
            return

        random_value = 0
        control_go_message = MessageDefinitions.create_control_go_message(MessageType.REQUEST, random_value)
        on_success = lambda response_message : self._execute_buffer_on_success(control_go_message, response_message)
        on_failure = lambda : self._execute_buffer_on_failure(control_go_message)
        channel.send_message(control_go_message, ack_required=True, on_success=on_success, on_failure=on_failure)

        for callback in self.callbacks_on_send:
            callback(control_go_message)


    def _execute_buffer_on_success(self, request_message : Message, response_message : Message):
        if response_message.data().type().identifier() != MessageDefinitions.CONTROL_GO_MESSAGE:
            ApplicationContext.error_manager.report_error("Response message is not a control go message", ErrorSeverity.WARNING)
            return
        
        print("Buffer executed successfully")
        self.buffer = []

    def _execute_buffer_on_failure(self, request_message : Message):
        print("Failed to execute buffer message, no response")


    def send_command_buffer(self, channel: CommunicationInterface):
        self._is_sending_buffer = True
        for message in self.buffer:
            # curry the message into the lambda function
            on_success_curry = lambda response_message : self._command_msg_on_success(message, response_message)
            on_failure_curry = lambda : self._command_msg_on_failure(message)

            self._is_waiting = True
            channel.send_message(message, ack_required=True, on_success=on_success_curry, on_failure=on_failure_curry)
            
            while self._is_waiting:
                channel.tick()


            for callback in self.callbacks_on_send:
                callback(message)


        if not self._successfully_sent:
            # if the buffer was not successfully sent, then we need to keep the buffer
            ApplicationContext.error_manager.report_error("Buffer was not successfully sent", ErrorSeverity.WARNING)
            self.clear_buffer(channel)
            return
        else:
            print("Buffer was successfully sent")
            self.execute_buffer(channel) # will clear the buffer once the buffer is executed
        
        self._is_sending_buffer = False

    def send_command_buffer_async(self, channel: CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot send buffer while sending buffer", ErrorSeverity.WARNING)
            return
        
        thread = threading.Thread(target=self.send_command_buffer, args=(channel,))
        thread.start()


    def _command_msg_on_success(self, request_message : Message, response_message : Message):
        if request_message.data().type().identifier() == MessageDefinitions.MOTOR_CONTROL_MESSAGE:
            # check that the response message is a motor event message
            if response_message.data().type().identifier() != MessageDefinitions.MOTOR_EVENT_MESSAGE:
                self._successfully_sent = False
                ApplicationContext.error_manager.report_error("Response message is not a motor event message", ErrorSeverity.WARNING)
                return

            if self._compare_motor_control_messages(request_message, response_message):
                self._successfully_sent = True
        elif request_message.data().type().identifier() == MessageDefinitions.SENSOR_EVENT_MESSAGE:
            # check that the response message is a sensor event message
            if response_message.data().type().identifier() != MessageDefinitions.SENSOR_EVENT_MESSAGE:
                ApplicationContext.error_manager.report_error("Response message is not a sensor event message", ErrorSeverity.WARNING)
                self._successfully_sent = False
                return

            if self._compare_sensor_event_messages(request_message, response_message):
                self._successfully_sent = True
        else:
            ApplicationContext.error_manager.report_error("Unknown message type", ErrorSeverity.WARNING)
            self._successfully_sent = False

        self._is_waiting = False


    def _command_msg_on_failure(self, request_message : Message):
        ApplicationContext.error_manager.report_error("Failed to send command message, no acknowledgement", ErrorSeverity.WARNING)
        self._successfully_sent = False
        self._is_waiting = False

    def _compare_motor_control_messages(self, request_message : Message, motor_event_response : Message):
        # check that the motor id is the same
        request_motor_id = request_message.get_field("motor_id").value()
        response_motor_id = motor_event_response.get_field("motor_id").value()
        if request_motor_id != response_motor_id:
            ApplicationContext.error_manager.report_error(f"Motor ID mismatch: {request_motor_id} != {response_motor_id}", ErrorSeverity.WARNING)
            return False
        
        # check that the control mode is the same
        request_control_mode = request_message.get_field("control_mode").value()
        response_control_mode = motor_event_response.get_field("event_type").value()
        if request_control_mode != response_control_mode:
            ApplicationContext.error_manager.report_error(f"Control mode mismatch: {request_control_mode} != {response_control_mode}", ErrorSeverity.WARNING)
            return False
        
        # check that the control value is the same
        request_control_value = request_message.get_field("control_value").value()
        response_control_value = motor_event_response.get_field("event_value").value()

        if request_control_value != response_control_value:
            ApplicationContext.error_manager.report_error(f"Control value mismatch: {request_control_value} != {response_control_value}", ErrorSeverity.WARNING)
            return False
        
    def _compare_sensor_event_messages(self, request: Message, response: Message):
        # check that the sensor id is the same
        request_sensor_id = request.get_field("sensor_id").value()
        response_sensor_id = response.get_field("sensor_id").value()
        if request_sensor_id != response_sensor_id:
            ApplicationContext.error_manager.report_error(f"Sensor ID mismatch: {request_sensor_id} != {response_sensor_id}", ErrorSeverity.WARNING)
            return False
        
        # check that the sensor value is the same
        request_sensor_value = request.get_field("sensor_value").value()
        response_sensor_value = response.get_field("sensor_value").value()
        if request_sensor_value != response_sensor_value:
            ApplicationContext.error_manager.report_error(f"Sensor value mismatch: {request_sensor_value} != {response_sensor_value}", ErrorSeverity.WARNING)
            return False

        return True
        
