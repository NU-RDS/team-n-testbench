from rdscom.rdscom import CommunicationChannel, Message, MessageType
from com.message_definitions import MessageDefinitions

import threading

class CommandBuffer:
    def __init__(self):
        self.buffer : list[Message] = []
        self._successfully_sent = False
        self._is_waiting = False
        self._is_sending_buffer = False

    def add_command(self, message: Message):
        self.buffer.append(message)

    def is_sending_buffer(self):
        return self._is_sending_buffer
    
    def clear_buffer(self, channel : CommunicationChannel):
        if self._is_sending_buffer:
            print("Cannot clear buffer while sending buffer")
            return

        # send a request to clear the buffer
        clear_buffer_message = MessageDefinitions.create_clear_buffer_message()
        on_success = lambda response_message : self._clear_buffer_on_success(clear_buffer_message, response_message)
        on_failure = lambda response_message : self._clear_buffer_on_failure(clear_buffer_message, response_message)
        
        channel.send(clear_buffer_message, ack_required=True, on_success=on_success, on_failure=on_failure)

    def _clear_buffer_on_success(self, request_message : Message, response_message : Message):        
        if response_message.data().type().identifier() != MessageDefinitions.CLEAR_BUFFER_MESSAGE:
            print("Response message is not a clear buffer message")
            return
        
        self.buffer = []

    def _clear_buffer_on_failure(self, request_message : Message, response_message : Message):
        print("Failed to clear buffer message")

    def execute_buffer(self, channel: CommunicationChannel):
        if self._is_sending_buffer:
            print("Cannot execute buffer while sending buffer")
            return

        random_value = 0
        control_go_message = MessageDefinitions.create_control_go_message(MessageType.REQUEST, random_value)
        on_success = lambda response_message : self._execute_buffer_on_success(control_go_message, response_message)
        on_failure = lambda response_message : self._execute_buffer_on_failure(control_go_message, response_message)
        channel.send(control_go_message, ack_required=True, on_success=on_success, on_failure=on_failure)


    def _execute_buffer_on_success(self, request_message : Message, response_message : Message):
        if response_message.data().type().identifier() != MessageDefinitions.CONTROL_GO_MESSAGE:
            print("Response message is not a control go message")
            return
        
        print("Buffer executed successfully")
        self.buffer = []

    def _execute_buffer_on_failure(self, request_message : Message, response_message : Message):
        print("Failed to execute buffer message")



    def send_command_buffer(self, channel: CommunicationChannel):
        self._is_sending_buffer = True
        for message in self.buffer:
            # curry the message into the lambda function
            on_success_curry = lambda response_message : self._command_msg_on_success(message, response_message)
            on_failure_curry = lambda response_message : self._command_msg_on_failure(message, response_message)

            self._is_waiting = True
            channel.send(message, ack_required=True, on_success=on_success_curry, on_failure=on_failure_curry)
            
            while self._is_waiting:
                pass # wait for the message to be sent


        if not self._successfully_sent:
            # if the buffer was not successfully sent, then we need to keep the buffer
            print("Buffer was not successfully sent, keeping buffer locally, clearing buffer remotely")
            self.clear_buffer(channel)
            return
        else:
        
        self._is_sending_buffer = False

        self.buffer = []

    def send_command_buffer_async(self, channel: CommunicationChannel):
        if self._is_sending_buffer:
            print("Buffer is already being sent")
            return
        
        self._is_sending_buffer = True
        thread = threading.Thread(target=self.send_command_buffer, args=(channel,))
        thread.start()



    def _command_msg_on_success(self, request_message : Message, response_message : Message):
        if request_message.data().type().identifier() == MessageDefinitions.MOTOR_CONTROL_MESSAGE:
            # check that the response message is a motor event message
            if response_message.data().type().identifier() != MessageDefinitions.MOTOR_EVENT_MESSAGE:
                self._successfully_sent = False
                return

            if self._compare_motor_control_messages(request_message, response_message):
                self._successfully_sent = True
        elif request_message.data().type().identifier() == MessageDefinitions.SENSOR_EVENT_MESSAGE:
            # check that the response message is a sensor event message
            if response_message.data().type().identifier() != MessageDefinitions.SENSOR_EVENT_MESSAGE:
                self._successfully_sent = False
                return

            if self._compare_sensor_event_messages(request_message, response_message):
                self._successfully_sent = True
        else:
            print("Unknown message type")
            self._successfully_sent = False

        self._is_waiting = False



    def _command_msg_on_failure(self, request_message : Message, response_message : Message):
        self._successfully_sent = False
        self._is_waiting = False

    def _compare_motor_control_messages(self, request_message : Message, motor_event_response : Message):
        # check that the motor id is the same
        request_motor_id = request_message.get_field("motor_id").value()
        response_motor_id = motor_event_response.get_field("motor_id").value()
        if request_motor_id != response_motor_id:
            return False
        
        # check that the control mode is the same
        request_control_mode = request_message.get_field("control_mode").value()
        response_control_mode = motor_event_response.get_field("event_type").value()
        if request_control_mode != response_control_mode:
            return False
        
        # check that the control value is the same
        request_control_value = request_message.get_field("control_value").value()
        response_control_value = motor_event_response.get_field("event_value").value()

        if request_control_value != response_control_value:
            return False
        
    def _compare_sensor_event_messages(self, request: Message, response: Message):
        # check that the sensor id is the same
        request_sensor_id = request.get_field("sensor_id").value()
        response_sensor_id = response.get_field("sensor_id").value()
        if request_sensor_id != response_sensor_id:
            return False
        
        # check that the sensor value is the same
        request_sensor_value = request.get_field("sensor_value").value()
        response_sensor_value = response.get_field("sensor_value").value()
        if request_sensor_value != response_sensor_value:
            return False

        return True
        
