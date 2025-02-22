#ifndef __STATE_MANAGER_H__
#define __STATE_MANAGER_H__


#include <Arduino.h>
#include "com_manager/com_manager.hpp"
#include "utils/led.hpp"

/// \brief The state of the system
enum State : uint8_t
{
    INIT,
    READY,
    ACTIVE,
    ERROR
};

class StateManager {

public:
    StateManager() = default;
    ~StateManager() = default;

    StateManager(ComManager &comms_manager)
        : comms_manager_(comms_manager),
          odrive0_heartbeat_timeout_(comms_manager_.odrive0_.odrive_user_data_.heartbeat_timeout),
          odrive1_heartbeat_timeout_(comms_manager_.odrive1_.odrive_user_data_.heartbeat_timeout)
        {}

    
    /// \brief Reboot the Teensy
    void reboot()
    {
        SCB_AIRCR = 0x05FA0004;
    }

    /// \brief Request estop from odrives
    void request_disable()
    {
        Estop_msg_t estop_msg;
        comms_manager_.odrive0_.odrive_.send(estop_msg);
        comms_manager_.odrive1_.odrive_.send(estop_msg);
    }

    /// \brief Process enable request, clear errors
    void request_enable()
    {
        clear_safe_errors(comms_manager_.odrive0_.odrive_, comms_manager_.odrive0_.odrive_user_data_.last_error);
        comms_manager_.odrive0_.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
        clear_safe_errors(comms_manager_.odrive1_.odrive_, comms_manager_.odrive1_.odrive_user_data_.last_error);
        comms_manager_.odrive1_.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
    }

    
    /// \brief Update the LED strip based on the current state and odrive timeouts
    void update_led()
    {

        switch (current_state)
        {
            case State::INIT:
                setColor(1, blue);
                break;
            case State::READY:
                setColor(1, yellow);
                break;
            case State::ACTIVE:
                setColor(1, green);
                break;
            case State::ERROR:
                setColor(1, red);
                break;
        }

        switch ((odrive0_heartbeat_timeout_ << 1) | odrive1_heartbeat_timeout_)
        {
            case 0b11: // Both ODrive 0 and ODrive 1 heartbeat timeouts
                setColor(2, red);
                break;
            case 0b10: // Only ODrive 0 heartbeat timeout
                setColor(2, cyan);
                break;
            case 0b01: // Only ODrive 1 heartbeat timeout
                setColor(2, magenta);
                break;
            case 0b00: // No ODrive heartbeat timeouts
                setColor(2, green);
                break;
        }
    }

    void stop_motors() {
        comms_manager_.odrive0_.set_torque(0.0);
        comms_manager_.odrive1_.set_torque(0.0);
    }

    bool check_errors() {
        return odrive0_heartbeat_timeout_ or
               odrive1_heartbeat_timeout_ or
               estop_enabled_ or
               (!clear_safe_errors(comms_manager_.odrive0_.odrive_, comms_manager_.odrive0_.odrive_user_data_.last_error)) or
               (!clear_safe_errors(comms_manager_.odrive1_.odrive_, comms_manager_.odrive1_.odrive_user_data_.last_error)) or
               (comms_manager_.odrive0_.odrive_user_data_.last_heartbeat.Axis_State != ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL) or
               (comms_manager_.odrive1_.odrive_user_data_.last_heartbeat.Axis_State != ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);

    }

    void execute_state() {

        switch (current_state)
        {
        case State::INIT:
            // Do Nothing
            break;
        
        case State::READY:
            // Do Nothing
            break;

        case State::ACTIVE:
            // Execute the demo (Need to include the function)
            break;

        case State::ERROR:
            // Do Nothing
            break;

        }

    }

    void enter_state(State state) {

        switch (state)
        {
        case State::INIT:
            request_enable();
            break;
        case State::READY:
            break;
        case State::ACTIVE:
            break;
        case State::ERROR:
            request_disable();
            // Check for communications with the ODrives
            if (comms_manager_.comms_timeout())
            {
                reboot();
            }
            break;
        }

    }

    void exit_state(State state) {

        switch (state)
        {
        case State::INIT:
            break;
        case State::READY:
            break;
        case State::ACTIVE:
            // Stop motors
            stop_motors();
            break;
        case State::ERROR:
            break;
        }

    }

    void change_state() {

    // Check for errors. If any error are found, change state to ERROR and return
    if (check_errors())
    {
        if (current_state == State::ERROR)
        {
            return;
        }
        exit_state(current_state);
        current_state = State::ERROR;
        enter_state(current_state);
        Serial.println("Switching to ERROR");
        return;
    }

        switch (current_state)
        {
        case State::INIT:
            // Check for the any critical errors,
            // then transition to READY if not switch to ERROR state
            if (not check_errors()) {
                exit_state(current_state);
                current_state = State::READY;
                enter_state(current_state);
                Serial.println("Switching to READY");
            }

            else {
                exit_state(current_state);
                current_state = State::ERROR;
                enter_state(current_state);
                Serial.println("Switching to ERROR");
            }

            break;
        
        case State::READY:
            // Transition to ERROR if any critical errors are found     
            if (check_errors()) {
                exit_state(current_state);
                current_state = State::ERROR;
                enter_state(current_state);
                Serial.println("Switching to ERROR");
            }

            // Transition to ACTIVE if the deadman switch is pressed
            if (deadman_switch_pressed_) {
                exit_state(current_state);
                current_state = State::ACTIVE;
                enter_state(current_state);
                Serial.println("Switching to ACTIVE");
            }


            break;

        case State::ACTIVE:
            // Transition to ERROR if any critical errors are found     
            if (check_errors()) {
                exit_state(current_state);
                current_state = State::ERROR;
                enter_state(current_state);
                Serial.println("Switching to ERROR");
            }
            
            // Transition to ACTIVE if the deadman switch is released
            if (not deadman_switch_pressed_)
            {
                exit_state(current_state);
                current_state = State::READY;
                enter_state(current_state);
                Serial.println("Switching to READY");
            }

            break;

        case State::ERROR:
            // 
            if (not comms_manager_.comms_timeout())
            {
                exit_state(current_state);
                current_state = State::INIT;
                enter_state(current_state);
                Serial.println("Switching to INIT");
            }
            break;

        }

    }

/// \brief Check the deadman switch state
void check_deadman()
{
    comms_manager_.tick();
    delay(100);

    if (digitalRead(DEADMAN_SWITCH) == LOW)
    {
        deadman_switch_pressed_ = false;
        return;
    }
    deadman_switch_pressed_ = true;
    return;
}



public:
    ComManager &comms_manager_;
    bool &odrive0_heartbeat_timeout_;
    bool &odrive1_heartbeat_timeout_;
    bool estop_enabled_ = false;
    bool deadman_switch_pressed_ = false;
    State current_state = State::INIT;

};

#endif // __STATE_MANAGER_H__