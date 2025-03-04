from rdscom.rdscom import CommunicationInterface, Message, MessageType, CommunicationInterface
from com.message_definitions import MessageDefinitions
from interface.error_manager import ErrorManager, ErrorSeverity
import threading
from interface.docks.control import ControlModes
from app_context import ApplicationContext

class CommandBuffer:
    def __init__(self):
        self.buffer : list[Message] = []
        self._successfully_sent = False
        self._is_waiting = False
        self._is_sending_buffer = False
        self._is_zeroing = False
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
    
    def load_buffer_from_file(self, file_path: str):
        self.buffer = []
        print(f"Loading buffer from file: {file_path}")
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                # print(f"Line: {line}")
                angles = line.split(",")
                # print(f"Angles: {angles}")

                if len(angles) < 2:
                    ApplicationContext.error_manager.report_error("Invalid line in buffer file", ErrorSeverity.WARNING)
                    break

                angle_1 = float(angles[0])
                angle_2 = float(angles[1])

                # create a message for each angle
                message_1 = MessageDefinitions.create_motor_control_message(MessageType.REQUEST, 0, ControlModes.POSITION, angle_1, True)
                message_2 = MessageDefinitions.create_motor_control_message(MessageType.REQUEST, 1, ControlModes.POSITION, angle_2, True)

                self.add_command(message_1)
                self.add_command(message_2)

    def clear_buffer(self, com : CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot clear buffer while sending buffer", ErrorSeverity.WARNING)
            return

        # send a request to clear the buffer
        clear_buffer_message = MessageDefinitions.create_clear_control_queue_message(MessageType.REQUEST, 0)
        on_success = lambda response_message : self._clear_buffer_on_success(clear_buffer_message, response_message)
        on_failure = lambda : self._clear_buffer_on_failure(clear_buffer_message)
        
        com.send_message(clear_buffer_message, ack_required=True, on_success=on_success, on_failure=on_failure)

        for callback in self.callbacks_on_send:
            callback(clear_buffer_message)

    def _clear_buffer_on_success(self, request_message : Message, response_message : Message):        
        if response_message.data().type().identifier() != MessageDefinitions.clear_control_queue_id():
            ApplicationContext.error_manager.report_error("Response message is not a clear buffer message", ErrorSeverity.WARNING)
            return
        
        self.buffer = []

    def _clear_buffer_on_failure(self, request_message : Message):
        ApplicationContext.error_manager.report_error("Failed to clear buffer message, no response", ErrorSeverity.WARNING)

    def execute_buffer(self, com: CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot execute buffer while sending buffer", ErrorSeverity.WARNING)
            return

        random_value = 0
        control_go_message = MessageDefinitions.create_control_go_message(MessageType.REQUEST, random_value)
        on_success = lambda response_message : self._execute_buffer_on_success(control_go_message, response_message)
        on_failure = lambda : self._execute_buffer_on_failure(control_go_message)
        com.send_message(control_go_message, ack_required=True, on_success=on_success, on_failure=on_failure)

        for callback in self.callbacks_on_send:
            callback(control_go_message)


    def _execute_buffer_on_success(self, request_message : Message, response_message : Message):
        if response_message.data().type().identifier() != MessageDefinitions.control_go_id():
            ApplicationContext.error_manager.report_error("Response message is not a control go message", ErrorSeverity.WARNING)
            return
        
        print("Buffer executed successfully")
        self.buffer = []

    def _execute_buffer_on_failure(self, request_message : Message):
        print("Failed to execute buffer message, no response")


    def send_command_buffer(self, com: CommunicationInterface):
        self._is_sending_buffer = True
        self._successfully_sent = True
        print(f"Sending buffer of size {len(self.buffer)}")
        for message in self.buffer:
            # curry the message into the lambda function
            on_success_curry = lambda response_message : self._command_msg_on_success(message, response_message)
            on_failure_curry = lambda : self._command_msg_on_failure(message)

            self._is_waiting = True
            com.send_message(message, ack_required=True, on_success=on_success_curry, on_failure=on_failure_curry)
            
            print("Begin waiting for response")
            while self._is_waiting:
                com.tick()
            print("End waiting for response")

            if not self._successfully_sent:
                ApplicationContext.error_manager.report_error("Failed to send command message, no acknowledgement. Stopping send early.", ErrorSeverity.WARNING)
                break

            for callback in self.callbacks_on_send:
                callback(message)

        self._is_sending_buffer = False
        print("Finished sending buffer")

        if not self._successfully_sent:
            # if the buffer was not successfully sent, then we need to keep the buffer
            ApplicationContext.error_manager.report_error("Buffer was not successfully sent", ErrorSeverity.WARNING)
            self.clear_buffer(com)
            return
        else:
            print("Buffer was successfully sent")
            self.execute_buffer(com) # will clear the buffer once the buffer is executed
        
        self._is_sending_buffer = False

    def send_command_buffer_async(self, com: CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot send buffer while sending buffer", ErrorSeverity.WARNING)
            return
        
        thread = threading.Thread(target=self.send_command_buffer, args=(com,))
        thread.start()


    def _command_msg_on_success(self, request_message : Message, response_message : Message):
        print("Command message success")
        self._is_waiting = False
        if request_message.data().type().identifier() == MessageDefinitions.motor_control_id():
            # check that the response message is a motor event message
            if response_message.data().type().identifier() != MessageDefinitions.motor_control_id():
                self._successfully_sent = False
                ApplicationContext.error_manager.report_error("Response message is not a motor event message", ErrorSeverity.WARNING)
                return

            if self._compare_motor_control_messages(request_message, response_message):
                self._successfully_sent = True
        elif request_message.data().type().identifier() == MessageDefinitions.sensor_datastream_id():
            # check that the response message is a sensor event message
            if response_message.data().type().identifier() != MessageDefinitions.sensor_datastream_id():
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
        response_control_mode = motor_event_response.get_field("control_mode").value()
        if request_control_mode != response_control_mode:
            ApplicationContext.error_manager.report_error(f"Control mode mismatch: {request_control_mode} != {response_control_mode}", ErrorSeverity.WARNING)
            return False
        
        # check that the control value is the same
        request_control_value = request_message.get_field("control_value").value()
        response_control_value = motor_event_response.get_field("control_value").value()

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
        

    def zero(self, com : CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot zero while sending buffer", ErrorSeverity.WARNING)
            return

        zero_message = MessageDefinitions.create_zero_command_message(MessageType.REQUEST, 0)
        on_success = lambda response_message : self._on_zero_success(response_message)
        on_failure = lambda : self._on_zero_failure()
        self._is_waiting = True
        self._successfully_sent = False
        com.send_message(zero_message, ack_required=True, on_failure=on_failure, on_success=on_success)
        while self._is_waiting:
            com.tick()

        if not self._successfully_sent:
            ApplicationContext.error_manager.report_error("Failed to send zero message", ErrorSeverity.WARNING)
            self._is_sending_buffer = False
            return
        
        self._is_zeroing = True
        # now we have to wait for the zero to complete
        while self._is_waiting:
            com.tick()
        
        self._is_zeroing = False

    def zero_async(self, com : CommunicationInterface):
        if self._is_sending_buffer:
            ApplicationContext.error_manager.report_error("Cannot zero while sending buffer", ErrorSeverity.WARNING)
            return

        thread = threading.Thread(target=self.zero, args=(com,))
        thread.start()
            
    def handle_zero_done(self, response_message : Message):
        # send back a response message
        response = Message.create_response(response_message, response_message.data())
        ApplicationContext.mcu_com.send_message(response)

        if response_message.data().type().identifier() != MessageDefinitions.zero_done_id():
            ApplicationContext.error_manager.report_error("Response message is not a zero command message", ErrorSeverity.WARNING)
            return
        
        success = response_message.data().get_field("success").value()
        if success == 0:
            ApplicationContext.error_manager.report_error("Zero failed", ErrorSeverity.WARNING)
        else:
            ApplicationContext.error_manager.report_error("Zero succeeded", ErrorSeverity.INFO)

        self._is_waiting = False

    def _on_zero_success(self, response_message : Message):
        self._is_waiting = False
        if response_message.data().type().identifier() != MessageDefinitions.zero_command_id():
            ApplicationContext.error_manager.report_error("Response message is not a zero command message", ErrorSeverity.WARNING)
            return
        
        success = response_message.data().get_field("success").value()
        if success == 0:
            ApplicationContext.error_manager.report_error("Zero failed", ErrorSeverity.WARNING)
            self._successfully_sent = False
        else:
            ApplicationContext.error_manager.report_error("Zero succeeded", ErrorSeverity.INFO)
            self._successfully_sent = True

    def _on_zero_failure(self):
        self._is_waiting = False
        self._successfully_sent = False
        ApplicationContext.error_manager.report_error("Failed to send zero message", ErrorSeverity.WARNING)
