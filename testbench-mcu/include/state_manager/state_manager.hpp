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
        : comms_manager(comms_manager),
          odrive0_heartbeat_timeout_(comms_manager.odrive0_.odrive_user_data_.heartbeat_timeout),
          odrive1_heartbeat_timeout_(comms_manager.odrive1_.odrive_user_data_.heartbeat_timeout)
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
        comms_manager.odrive0_.odrive_.send(estop_msg);
        comms_manager.odrive1_.odrive_.send(estop_msg);
    }

    /// \brief Process enable request, clear errors
    void request_enable()
    {
        clear_safe_errors(comms_manager.odrive0_.odrive_, comms_manager.odrive0_.odrive_user_data_.last_error);
        comms_manager.odrive0_.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
        clear_safe_errors(comms_manager.odrive1_.odrive_, comms_manager.odrive1_.odrive_user_data_.last_error);
        comms_manager.odrive1_.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
    }

    
    /// \brief Update the LED strip based on the current state and odrive timeouts
    void ledUpdate()
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
                setColor(3, red);
                break;
            case 0b10: // Only ODrive 0 heartbeat timeout
                setColor(3, cyan);
                break;
            case 0b01: // Only ODrive 1 heartbeat timeout
                setColor(3, magenta);
                break;
            case 0b00: // No ODrive heartbeat timeouts
                setColor(3, green);
                break;
        }
    }

public:
    ComManager &comms_manager;
    bool &odrive0_heartbeat_timeout_;
    bool &odrive1_heartbeat_timeout_;
    bool estop_enabled = false;
    bool deadman_switch_pressed = false;
    State current_state = State::INIT;

};

#endif // __STATE_MANAGER_H__