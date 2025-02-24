#ifndef __FINGER_MANAGER_H__
#define __FINGER_MANAGER_H__

#ifdef CAN_ERROR_BUS_OFF
#undef CAN_ERROR_BUS_OFF
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846
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
 * @struct PhiVal
 * @brief Stores adjusted phi values
 */
class PhiVal
{
public:
    float last_phi0;
    float last_phi1;
    float adjusted_phi0;
    float adjusted_phi1;
    int cycles0 = 0;
    int cycles1 = 0;
    std::vector<float> adjust_phi_vals(std::vector<float> phi);
};

std::vector<float> PhiVal::adjust_phi_vals(std::vector<float> phi) 
    {
        const float current_phi_0 = phi.at(0);
        const float current_phi_1 = phi.at(1);

        // If we are crossing a full rotation, we adjust the cycle count
        if (last_phi0 > 0.0f && current_phi_0 < 0.0f) 
        {
            cycles0++;  // Completed a cycle
        }
        else if (last_phi0 < 0.0f && current_phi_0 > 0.0f) 
        {
            cycles0--;  // Completed a cycle in reverse direction
        }

        // If we are crossing a full rotation, we adjust the cycle count
        if (last_phi1 > 0.0f && current_phi_1 < 0.0f) 
        {
            cycles1++;  // Completed a cycle
        }
        else if (last_phi1 < 0.0f && current_phi_1 > 0.0f) 
        {
            cycles1--;  // Completed a cycle in reverse direction
        }

        // Update previous and current angles
        last_phi0 = current_phi_0;
        last_phi1 = current_phi_1;

        adjusted_phi0 = current_phi_0 + cycles0 * M_PI * 2;
        adjusted_phi1 = current_phi_1 + cycles1 * M_PI * 2;
        return {adjusted_phi0, adjusted_phi1};
    }

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

    /// @brief Get phi values
    PhiVal adjusted_phi();

    /// @brief Get finger data
    FingerData get_finger_data();

public:
    FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0_; /// CAN bus for first ODrive
    FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1_; /// CAN bus for second ODrive
    ODriveManager<CAN2> &odrive0_; /// Address of first ODrive
    ODriveManager<CAN3> &odrive1_; /// Address of second ODrive
};

FingerManager::FingerManager(
    FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_256> &canbus0,
    FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_256> &canbus1,
    ODriveManager<CAN2> &odrive0,
    ODriveManager<CAN3> &odrive1,
    _MB_ptr callback_odrive0,
    _MB_ptr callback_odrive1)
    : canbus0_(canbus0), canbus1_(canbus1), odrive0_(odrive0), odrive1_(odrive1) {
    
    canbus0_.begin();
    canbus0_.setBaudRate(CAN_BAUDRATE);
    canbus0_.setMaxMB(16);
    canbus0_.enableFIFO();
    canbus0_.enableFIFOInterrupt();
    canbus1_.onReceive(callback_odrive0);

    canbus1_.begin();
    canbus1_.setBaudRate(CAN_BAUDRATE);
    canbus1_.setMaxMB(16);
    canbus1_.enableFIFO();
    canbus1_.enableFIFOInterrupt();
    canbus1_.onReceive(callback_odrive1);
}

bool FingerManager::initialize() {
    bool odrive0_found = find_odrive(odrive0_);
    bool odrive1_found = find_odrive(odrive1_);

    if (!odrive0_found || !odrive1_found) {
        Serial.println("ERROR: Failed to find one or both ODrives. Initialization aborted");
        return false;
    }

    odrive0_.startup_odrive_checks();
    odrive1_.startup_odrive_checks();

    bool odrive0_started = startup_odrive(odrive0_);
    bool odrive1_started = startup_odrive(odrive1_);

    if (!odrive0_started || !odrive1_started) {
        Serial.println("ERROR: Failed to start one or both ODrives. Initialization aborted");
        return false;
    }

    Serial.println("Initialization successful");
    return true;
}

void FingerManager::tick() {
    pumpEvents(canbus0_);
    pumpEvents(canbus1_);

    odrive0_.odrive_user_data_.heartbeat_timeout = (millis() - odrive0_.odrive_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
    odrive1_.odrive_user_data_.heartbeat_timeout = (millis() - odrive1_.odrive_user_data_.last_heartbeat_time) > ODRIVE_HEARTBEAT_TIMEOUT;
}

bool FingerManager::comms_timeout() {
    return odrive0_.odrive_user_data_.heartbeat_timeout || 
           odrive1_.odrive_user_data_.heartbeat_timeout;
}


template <typename T>
bool FingerManager::find_odrive(T &odrive) {
    Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id));

    unsigned long start_time = millis();
    while (!odrive.odrive_user_data_.received_heartbeat) {
        tick();
        delay(100);
        Serial.println("Waiting for ODrive" + String(odrive.odrive_user_data_.node_id));

        if (millis() - start_time > odrive_timeout) {
            Serial.println("ERROR: Timeout while waiting for ODrive" + String(odrive.odrive_user_data_.node_id));
            return false;
        }
    }

    Serial.println("Found ODrive" + String(odrive.odrive_user_data_.node_id));
    return true;
}

template <typename T>
bool FingerManager::startup_odrive(T &odrive) {
    Serial.println("Enabling closed loop control");
    unsigned long start_time = millis();

    while (odrive.odrive_user_data_.last_heartbeat.Axis_State != ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL) {
        delay(1);
        odrive.odrive_.setState(ODriveAxisState::AXIS_STATE_CLOSED_LOOP_CONTROL);
        
        for (int i = 0; i < 15; ++i) {
            delay(10);
            tick();
        }

        if (millis() - start_time > odrive_timeout) {
            Serial.println("ERROR: Timeout while enabling closed loop control for ODrive" + String(odrive.odrive_user_data_.node_id));
            return false;
        }
    }

    Serial.println("ODrive" + String(odrive.odrive_user_data_.node_id) + " running");
    return true;
}

std::vector<float> FingerManager::soft_limit_joints(std::vector<float> joint_thetas)
{
    const float joint_0_d_t = -discouraging_stiffness * joint_0_soft_limits.over_limits(joint_thetas.at(0));
    const float joint_1_d_t = -discouraging_stiffness * joint_1_soft_limits.over_limits(joint_thetas.at(1));

    return {joint_0_d_t, joint_1_d_t};
}

std::vector<float> FingerManager::phi_to_theta(std::vector<float> phi)
{
    std::vector<float> adjusted_phi_vals = adjusted_phi().adjust_phi_vals(phi);
    const float phi_0 = phi.at(0);
    const float phi_1 = phi.at(1);
    const float theta_0 = phi_0 * t1 + joint_0_cali_offset;
    const float theta_1 = phi_0 * t2 + phi_1 * t3 + joint_1_cali_offset;
    return {theta_0, theta_1};
}

std::vector<float> FingerManager::theta_to_phi(std::vector<float> joint_thetas)
{
    const float theta_0 = joint_thetas.at(0) - joint_0_cali_offset;
    const float theta_1 = joint_thetas.at(1) - joint_1_cali_offset;
    const float phi_0 = it1 * theta_0 + it2 * theta_1;
    const float phi_1 = it3 * theta_1;
    return {phi_0, phi_1};
}

std::vector<float> FingerManager::theta_to_torque(std::vector<float> theta_dif, std::vector<float> theta_dot_dif) 
{
    const float tau_0 = kp * theta_dif.at(0) - kd * theta_dot_dif.at(0);
    const float tau_1 = kp * theta_dif.at(1) - kd * theta_dot_dif.at(0);
    const float torque_0 = t1 * tau_0 + t2 * tau_1;
    const float torque_1 = t3 * tau_1;
    return {torque_0, torque_1};
}

bool FingerManager::move_js(std::vector<float> theta_des) 
{
    // Get position difference
    const float phi_0 = odrive0_.odrive_user_data_.last_feedback.Pos_Estimate;
    const float phi_1 = odrive1_.odrive_user_data_.last_feedback.Pos_Estimate; 
    const float phi_dot_0 = odrive0_.odrive_user_data_.last_feedback.Vel_Estimate;
    const float phi_dot_1 = odrive1_.odrive_user_data_.last_feedback.Vel_Estimate;
    std::vector<float> joint_thetas = phi_to_theta({phi_0, phi_1});
    std::vector<float> joint_thetas_dot = phi_to_theta({phi_dot_0, phi_dot_1});
    joint_thetas = soft_limit_joints(joint_thetas);

    // Check if within tolerance
    if (float_close_compare(theta_des.at(0), joint_thetas.at(0), 1e-3) and float_close_compare(theta_des.at(1), joint_thetas.at(1), 1e-3)) {
        return true;
    }

    const float theta_0_dif = theta_des.at(0) - joint_thetas.at(0);
    const float theta_1_dif = theta_des.at(1) - joint_thetas.at(1);
    // const float theta_0_dif_dot = 

    // Send joints and get motor torque
    const std::vector<float> torques = theta_to_torque({theta_0_dif, theta_1_dif}, {0.0, 0.0});

    // Send torque
    const float torque_0 = limit<float>(torques.at(0), motor_torque_limit);
    const float torque_1 = limit<float>(torques.at(1), motor_torque_limit);
    odrive0_.odrive_.setTorque(torque_0);
    odrive1_.odrive_.setTorque(torque_1);
    return false;
}

bool FingerManager::zero() 
{
    float prev_velocity_motor0 = 0.0f, current_velocity_motor0 = 0.0f;
    float prev_velocity_motor1 = 0.0f, current_velocity_motor1 = 0.0f;
    bool motor0_zeroed{false}, motor1_zeroed{false};

    unsigned long start_time = millis();
    const unsigned long zeroing_timeout = 10000;  // 10-second timeout to prevent infinite loops

    while (((not motor0_zeroed) or (not motor1_zeroed)) and (millis() - start_time) < zeroing_timeout) {

        // Get the latest velocity readings
        prev_velocity_motor0 = current_velocity_motor0;
        prev_velocity_motor1 = current_velocity_motor1;
        current_velocity_motor0 = odrive0_.odrive_user_data_.last_feedback.Vel_Estimate;
        current_velocity_motor1 = odrive1_.odrive_user_data_.last_feedback.Vel_Estimate;

        // Check if velocity is close to zero for motor 0
        if (!motor0_zeroed && float_close_compare(current_velocity_motor0, prev_velocity_motor0, 1e-4)) {
            motor0_zeroed = true;
            odrive0_.set_torque(0.0f);  // Stop applying torque
        } else if (!motor0_zeroed) {
            odrive0_.set_torque(zeroing_motor_torque_limit);
        }

        // Check if velocity is close to zero for motor 1
        if (!motor1_zeroed && float_close_compare(current_velocity_motor1, prev_velocity_motor1, 1e-4)) {
            motor1_zeroed = true;
            odrive1_.set_torque(0.0f);  // Stop applying torque
        } else if (!motor1_zeroed) {
            odrive1_.set_torque(-zeroing_motor_torque_limit);
        }

        // Small delay to allow ODrive feedback updates
        delay(10);
    }

    // Return true only if both motors have reached their zeroed state
    return motor0_zeroed and motor1_zeroed;
}


FingerData FingerManager::get_finger_data() {
    FingerData finger_data;

    // Store position estimates
    finger_data.motor_pos_estimates[0] = odrive0_.odrive_user_data_.last_feedback.Pos_Estimate;
    finger_data.motor_pos_estimates[1] = odrive1_.odrive_user_data_.last_feedback.Pos_Estimate;

    // Store velocity estimates
    finger_data.motor_vel_estimates[0] = odrive0_.odrive_user_data_.last_feedback.Vel_Estimate;
    finger_data.motor_vel_estimates[1] = odrive1_.odrive_user_data_.last_feedback.Vel_Estimate;

    // Store motor temperature estimates
    finger_data.motor_temp_estimates[0] = odrive0_.odrive_user_data_.last_temperature.Motor_Temperature;
    finger_data.motor_temp_estimates[1] = odrive0_.odrive_user_data_.last_temperature.Motor_Temperature;

    // Store joint angle estimates
    std::vector<float> phi = theta_to_phi({finger_data.motor_pos_estimates[0], finger_data.motor_pos_estimates[1]});
    finger_data.estimated_joint_angles[0] = phi[0]; 
    finger_data.estimated_joint_angles[1] = phi[1]; 

    return finger_data;
}

#endif // __FINGER_MANAGER_H__
