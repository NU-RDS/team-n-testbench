# Messages

This document details all of the messages that can be sent between the GUI and the MCU. We use the `rdscom` library to send these messages, if you want to learn more about the library, see the [rdscom repository](https://github.com/evan-bertis-sample/rdscom).

`rdscom` follows the idea of `DataPrototypes`, which describe how the data is structured (in key-value pairs). Each `DataPrototype` has a unique ID, which is used to identify the message. The GUI and the MCU both have a list of `DataPrototypes` that they can send and receive. These messages can be of type `Request`, `Response`, or `Error`. Some of these messages require acknowledgement, which is handled by the `rdscom` library.

## DataPrototypes

### `DataPrototype` 0 - `Heartbeat`
This message is used to check if the connection is still alive. The GUI sends a request to the MCU, and the MCU responds with an acknowledgement of type `Heartbeat`.

```
Message ID: 0
Fields:
    - `rand`: `int8` - A random number that the GUI generates to check if the connection is still alive
Acknowledgement: Yes
```

### `DataPrototype` 1 - `MotorControl`
This message is used to control the motors. The GUI sends a request to the MCU, and the MCU responds with an acknowledgement of type `MotorEvent`. **However,** this action isn't instataneous, rather it adds the control to a queue, which is triggered by the `ControlGo` message.

```
Message ID: 1
Fields:
    - `motor_id`: `uint8` - The ID of the motor to control
    - `control_mode`: `uint8` - The control mode of the motor (0: position, 1: velocity, 2: torque)
    - `control_value`: `float` - The value to set the motor to
    - `simutaneous`: `bool` - Whether the control should be executed simutaneously with the previous control in the queue
Acknowledgement: Yes
```

### `DataPrototype` 2 - `MotorEvent`
This message is used to send events from the MCU to the GUI. The MCU sends a response to the GUI after receiving a `MotorControl` message.

```
Message ID: 2
Fields:
    - `motor_id`: `uint8` - The ID of the motor that the event is for
    - `success`: `bool` - Whether the event was successful
    - `event_type`: `uint8` - The type of event (0: position, 1: velocity, 2: torque)
    - `event_value`: `float` - The value of the event
    - `num_in_queue`: `uint8` - The number of events in the queue
    - `executed_with_count`: `uint8` - The number of events executed with this event
Acknowledgement: No
```

### `DataPrototype` 3 - `ControlGo`
This message is used to trigger the execution of the control queue. The GUI sends a request to the MCU, and the MCU responds with an acknowledgement of type `ControlGo`.

```
Message ID: 3
Fields:
    - `rand`: `int8` - A random number that the GUI generates to check if the connection is still alive
Acknowledgement: Yes
```

### `DataPrototype` 4 - `ControlDone`
This message is used to send a response from the MCU to the GUI after the control queue has been executed. The MCU sends a response to the GUI after the control queue has been executed, and the GUI responds with an acknowledgement of type `ControlDone`.

```
Message ID: 4
Fields:
    - `success`: `bool` - Whether the control queue was executed successfully
    - `time`: `uint32` - The time it took to execute the control queue in milliseconds
    - `executed`: `uint8` - The number of events executed
Acknowledgement: Yes
```

### `DataPrototype` 5 - `StartSensorDatastream`
This message is used to start the sensor datastream. The GUI sends a request to the MCU, and the MCU responds with an acknowledgement of type `SensorDatastream`.

````
Message ID: 5
Fields:
    - `joint_id`: `uint8` - The ID of the sensor to start the datastream for, 255 for all sensors
    - `frequency`: `uint8` - The frequency of the datastream in Hz
Acknowledgement: Yes
````

### `DataPrototype` 6 - `SensorDatastream`
This message is used to send sensor data from the MCU to the GUI. The MCU sends a response to the GUI after receiving a `StartSensorDatastream` message.

````
Message ID: 6
Fields:
    - `joint_id`: `uint8` - The ID of the sensor that the data is for
    - `data`: `float` - The data from the sensor
Acknowledgement: No
````

### `DataPrototype` 7 - `StopSensorDatastream`
This message is used to stop the sensor datastream. The GUI sends a request to the MCU, and the MCU responds with an acknowledgement of type `SensorDatastream`.

````
Message ID: 7
Fields:
    - `joint_id`: `uint8` - The ID of the sensor to stop the datastream for, 255 for all sensors
Acknowledgement: Yes
````

### `DataPrototype` 8 - `ClearControlQueue`
This message is used to clear the control queue. The GUI sends a request to the MCU, and the MCU responds with an acknowledgement of type `ClearControlQueue`.

````
Message ID: 8
Fields:
    - `rand`: `int8` - A random number that the GUI generates to check if the connection is still alive
Acknowledgement: Yes
````

### `DataPrototype` 9 - `Error`
This message is used to send an error message from the MCU to the GUI. The MCU sends a response to the GUI when an error occurs, and the GUI responds with an acknowledgement of type `Error`.

````
Message ID: 9
Fields:
    - `error_code`: `uint8` - The error code
Acknowledgement: Yes
````

### `DataPrototype` 10 - `Stop`
This message is used to stop the motors. The GUI sends a request to the MCU, and the MCU responds with an acknowledgement of type `Stop`. This will override any control in the queue.

````
Message ID: 10
Fields:
    - `rand`: `int8` - A random number that the GUI generates to check if the connection is still alive
Acknowledgement: Yes
````

## Usage

So, if we wanted to make the end effector move to a certain position, we would send the following messages:

1. GUI sends a `MotorControl` message for all necessary motors to the MCU
2. GUI sends a `ControlGo` message to the MCU
3. MCU sends a `ControlDone` message to the GUI

If we wanted to start the sensor datastream for all sensors, we would send the following messages:

1. GUI sends a `StartSensorDatastream` message to the MCU
2. MCU sends a `SensorDatastream` message to the GUI for each sensor
3. GUI sends a `StopSensorDatastream` message to the MCU
