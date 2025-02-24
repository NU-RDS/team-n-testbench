#ifndef __FINGER_MANAGER_H__
#define __FINGER_MANAGER_H__

#ifdef CAN_ERROR_BUS_OFF
#undef CAN_ERROR_BUS_OFF
#endif

#include "odrive_manager/odrive_manager.hpp"
#include "robot_description/finger.hpp"
#include <Arduino.h>
#include <math.h>

/// @brief Odrive detection timeout in seconds (1 sec)
static const unsigned long odrive_timeout = 1000;

/// @brief Zeroing timeout in seconds (10 seconds)
static const unsigned long zeroing_timeout = 10000;


/**
 * @struct FingerData
 * @brief Stores sensor and computed data for a robotic finger
 */
struct FingerData
{
    /**
     * @brief Position estimates from motor encoders
     * @details Stores the most recent position estimates for both ODrives
     */
    float motor_pos_estimates[2];

    /**
     * @brief Velocity estimates from motor encoders
     * @details Stores the most recent velocity estimates for both ODrives
     */
    float motor_vel_estimates[2];

    /**
     * @brief Temperature estimates of motors
     * @details Stores the most recent temperature readings from both ODrives
     */
    float motor_temp_estimates[2];

    /**
     * @brief Computed joint angles
     * @details Stores the calculated joint angles based on encoder readings
     */
    float estimated_joint_angles[2];
};

/**
 * @class FingerManager
 * @brief Manages communication for two CAN buses controlling robotic fingers
 */
class FingerManager {
public:
    /// @brief Default Constructor
    FingerManager() = default;

    /**
     * @brief Parameterized constructor to initialize CAN buses and ODrive managers
     * @param canbus0 Reference to CAN bus 0
     * @param canbus1 Reference to CAN bus 1
     * @param odrive0 Reference to ODriveManager for CAN bus 0
     * @param odrive1 Reference to ODriveManager for CAN bus 1
     */
    FingerManager(
        FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0,
        FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1,
        ODriveManager<CAN2> &odrive0,
        ODriveManager<CAN3> &odrive1,
        _MB_ptr callback_odrive0,
        _MB_ptr callback_odrive1);

    bool initialize();
    void tick();
    bool comms_timeout();

    /**
     * @brief Generic CAN message handler
     * @param msg The received CAN message
     * @param odrive The ODriveManager instance to handle the message
     */
    template <typename T>
    void can_message_callback(const CAN_message_t &msg, T &odrive);

    /// @brief Finds an ODrive by checking for heartbeat messages
    template <typename T>
    bool find_odrive(T &odrive);

    /// @brief Enables closed-loop control for an ODrive
    template <typename T>
    bool startup_odrive(T &odrive);

    /** 
     * @brief Changes the desired joint angles if angles are over the soft limits
     * @param joint_thetas 
     * @return damped new joint angles
     */ 
    std::vector<float> soft_limit_joints(std::vector<float> joint_thetas);

    /// @brief Determines the joint angles (including the offset values)
    /// @param phi position or velocity of the motor (either)
    /// @returns joint angles
    std::vector<float> phi_to_theta(std::vector<float> phi);

    /// @brief Determines the motor angles (including the offset values)
    /// @param joint_thetas either the position or velocities of the joints (either)
    /// @returns motor angles
    std::vector<float> theta_to_phi(std::vector<float> joint_thetas);

    /// @brief Determines desired tau to send to motors
    /// @param theta_dif, theta_dot_dif parameters for pd controller
    /// @returns desired torque
    std::vector<float> theta_to_torque(std::vector<float> theta_dif, std::vector<float> theta_dot_dif);

    /// @brief Moves J0 and J1 to desired angles.
    /// @param theta_des desired angles for both joints (rad) 
    /// @returns boolean to indicate whether angles are within tolerance
    bool move_js(std::vector<float> theta_des);

    /**
     * @brief Calibrates the joints to motor angles
     * @returns Boolean to indicate success
     */
    bool zero();

    /// @brief Get finger data
    FingerData get_finger_data();

public:
    FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0_; /// CAN bus for first ODrive
    FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1_; /// CAN bus for second ODrive
    ODriveManager<CAN2> &odrive0_; /// Address of first ODrive
    ODriveManager<CAN3> &odrive1_; /// Address of second ODrive
};


#endif // __FINGER_MANAGER_H__
