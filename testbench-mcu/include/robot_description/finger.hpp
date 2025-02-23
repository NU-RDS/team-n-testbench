#pragma once
#include <math.h>
#include <vector>

#include "utils/angles.hpp"
#include "utils/helpers.hpp"
#include "utils/matrix.hpp"

/// @brief Maximum torque values
static const float max_torque = 0.036; // Hard maximum

/// @brief PD gains
const auto kp = 0.005;
const auto kd = 0.002;

/// @brief Link lengths in m
static constexpr float link_1_length = 44.165e-03; // link lengths in meters
static constexpr float link_2_length = 51.208e-03;

/// @brief Important radii
static const float r_motor = 0.005; // 10 mm diameter shaft of otor
static const float r_idler = 0.01; // 20 mm diameter idler pulley
static const float r_pulley = 0.01; // 20 mm diameter pulley

/// @note The transmission ratio of joint : motor 
static constexpr float transmission_1 = r_motor / r_pulley;
static constexpr float transmission_2 = -r_motor / r_idler;
static constexpr float transmission_3 = r_motor / r_pulley;


// [  t1  0  ]
// [  t2  t3 ]

/// @brief Joint limits in radians
// TODO: ACTUALLY CHECK LIMITS
static constexpr Limits<float> joint_1_limits = convert_angular_units(
    {0.0, 90.0},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);
static constexpr Limits<float> joint_2_limits = convert_angular_units(
    {0.0, 90.0},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);

static constexpr Limits<float> joint_1_soft_limits = convert_angular_units(
    {15.0, 70.0},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);
static constexpr Limits<float> joint_2_soft_limits = convert_angular_units(
    {15.0, 70.0},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);

// /// @brief Torque limit in N-m
// static constexpr float motor_torque_limit = 0.036f; // N*m

/// @brief Joint calibration offset angle (calculated on startup)
static constexpr float joint_1_cali_offset = convert_angular_units(
    0.0, AngleUnits::DEGREES,
    AngleUnits::RADIANS);

static constexpr float joint_2_cali_offset = convert_angular_units(
    0.0, AngleUnits::DEGREES,
    AngleUnits::RADIANS);

/// @brief Joint 1 velocity limits
static constexpr Limits<float> joint_1_vel_limits{-10.0, 10.0};
/// @brief Joint 2 velocity limits
static constexpr Limits<float> joint_2_vel_limits{-10.0, 10.0};

/// @brief Performs forward kinematics for the finger.
/// @param joint_angles {theta_1, theta_2} in radians for the joints.
/// @returns {x, y, z} of the end effector.
std::vector<float> forward_kinematics(std::vector<float> joint_angles)
{
    const auto theta_0 = joint_angles.at(0);
    const auto theta_1 = joint_angles.at(1);

    const float xe = link_1_length * cos(theta_0) + 
                     link_2_length * cos(theta_0 + theta_1);
    const float ye = 0.0;

    // TODO: check last line
    const float ze = link_1_length * sin(theta_0) +
                     link_2_length * sin(theta_0 + theta_1); 

    return {xe, ye, ze};
}

/// @brief Performs inverse kinematics for 2R finger.
/// @param pos {x, y, z} in meters of the end effector.
/// @returns {theta_1, theta_2} of the joints in radians required to move to the location.
std::vector<float> inverse_kinematics(std::vector<float, float, float> pos)
{
    // Check joint space of robot
    const auto radius2 = pos.at(0) * pos.at(0) + pos.at(2) * pos.at(2); // radius squared
    const auto radius = std::sqrt(radius2); // radius of finger
    if ((radius > link_1_length + link_2_length) || (radius < link_1_length - link_2_length)) {
        // invalid ik - outside of joint space
        return {nanf, nanf}; // invalid result
    }

    // Calculate relevant angles
    const auto gamma = std::atan2(pos.at(2), pos.at(0));
    const auto alpha = std::acos((radius2 + link_1_length * link_1_length - link_2_length * link_2_length) /
                                 (2 *radius * link_1_length));
    const auto beta = std::acos((link_1_length * link_1_length + link_2_length * link_2_length - radius2) /
                                (2 * link_1_length * link_2_length));
    
    // Calculate desired theta values
    const auto theta_0_1 = gamma - alpha; // theta 0, solution 1
    const auto theta_0_2 = gamma + alpha; // theta 0, solution 2
    const auto theta_1_1 = M_PI - beta; // theta 1, solution 1
    const auto theta_1_2 = beta - M_PI; // theta 1, solution 2

    // Check validity of theta angles
    bool solution_1 = false;
    bool solution_2 = false;
    if ((joint_1_limits.over_limits(theta_0_1) == 0.0) and (joint_2_limits.over_limits(theta_1_1) == 0.0)) {
        solution_1 = true;
    } 
    if ((joint_1_limits.over_limits(theta_0_2) == 0.0) and (joint_2_limits.over_limits(theta_1_2) == 0.0)) {
        solution_2 = true;
    } 

    // If two available, prefer normal bending motion
    if (solution_1 and solution_2) {
        // Prefer theta_2 < 0
        // TODO: CHANGE TO ONLY VALID JOINT WITH LIMITS
        if (theta_1_1 < theta_1_2) {
            return {theta_0_1, theta_1_1}; 
        } else {
            return {theta_0_2, theta_1_2};
        }
    } 
    
    if (solution_1) {
        return {theta_0_1, theta_1_2};
    }

    if (solution_2) {
        return {theta_0_2, theta_1_2};
    }

    return {nanf, nanf};
}


/// @brief Determines the joint angles given the motor angles
/// @param motor_vars either the position or velocity of the motor (either)
/// @returns {theta_1, theta_2} or {theta_1_dot, theta_2_dot}
std::vector<float> motors_to_joints(std::vector<float> motor_vars)
{
    const auto phi_0 = motor_vars.at(0);
    const auto phi_1 = motor_vars.at(1);
    const auto theta_0 = phi_0 * transmission_1;
    const auto theta_1 = phi_0 * transmission_2 + phi_1 * transmission_3;
    return {theta_0, theta_1};
}

/// @brief Determines the motor angles given the joint angles
/// @param joint_vars either the position or velocity of the joints (either)
/// @returns {phi_1, phi_2} or {phi_1_dot, phi_2_dot}
std::vector<float> joints_to_motors(std::vector<float> joint_vars)
{
    const auto theta_0 = joint_vars.at(0);
    const auto theta_1 = joint_vars.at(1);
    const auto phi_0 = transmission_1 * theta_0 + transmission_2 * theta_1;
    const auto phi_1 = transmission_3 * theta_1;
    return {phi_0, phi_1};
}

/// @brief Determines the joint angles (including the offset values)
/// @param motor_phis position or velocity of the motor (either)
/// @returns joint angles
std::vector<float> phi_to_theta(std::vector<float> motor_phis)
{
    auto joint_thetas = motors_to_joints(motor_phis);
    joint_thetas.at(0) += joint_1_cali_offset;
    joint_thetas.at(1) += joint_2_cali_offset;
    return joint_thetas;
}

/// @brief Determines the motor angles (including the offset values)
/// @param joint_thetas either the position or velocities of the joints (either)
/// @returns motor angles
std::vector<float> theta_to_phi(std::vector<float> joint_thetas)
{
    joint_thetas.at(0) -= joint_1_cali_offset;
    joint_thetas.at(1) -= joint_2_cali_offset;
    const auto motor_phis = joints_to_motors(joint_thetas);
    return motor_phis;
}

/// @brief Determines the motor torque values to send given the desired joint torques
/// @param joint_taus desired joint torque applied
/// @returns motor torque
std::vector<float> tau_to_torque(std::vector<float> joint_taus)
{
    const auto tau_0 = joint_taus.at(0);
    const auto tau_1 = joint_taus.at(1);

    const auto torque_0 = transmission_1 * tau_0 + transmission_2 * tau_1;
    const auto torque_1 = transmission_3 * tau_1;

    return {torque_0, torque_1};
}

/// @brief Determines the joint torque values to send given the motor torques
/// @param motor_torques desired motor torque
/// @returns joint torque
std::vector<float> torque_to_tau(std::vector<float> motor_torques)
{
    const auto torque_0 = motor_torques.at(0);
    const auto torque_1 = motor_torques.at(1);

    const auto tau_0 = transmission_1 * torque_0;
    const auto tau_1 = transmission_2 * torque_0 + transmission_3 * torque_1;

    return {tau_0, tau_1};
}

/// @brief Determines desired tau to send to motors
/// @param theta_dif, theta_dot_dif parameters for pd controller
/// @returns desired tau
std::vector<float> theta_to_tau(std::vector<float> theta_dif, std::vector<float> theta_dot_dif) {
    const auto tau0 = kp * theta_dif.at(0) - kd * theta_dot_dif.at(0);
    const auto tau1 = kp * theta_dif.at(1) - kd * theta_dot_dif.at(0);
    return {tau0, tau1};
}

// Matrix spatial_jacobian(std::vector<float> joint_angles)
// {
//     const auto theta_0 = joint_angles.at(0);
//     const auto theta_1 = joint_angles.at(1);
//     const auto theta_2 = joint_angles.at(2);

//     Matrix J_s(2, 3);

//     J_s(
//         0,
//         0) = -link_0_length * sin(theta_0) - link_1_length * sin(theta_0 + theta_1) - link_2_length * sin(theta_0 + theta_1 + theta_2);
//     J_s(0, 1) = -link_1_length * sin(theta_0 + theta_1) - link_2_length * sin(
//                                                                               theta_0 + theta_1 + theta_2);
//     J_s(0, 2) = -link_2_length * sin(theta_0 + theta_1 + theta_2);
//     J_s(
//         1,
//         0) = -link_0_length * cos(theta_0) - link_1_length * cos(theta_0 + theta_1) - link_2_length * cos(theta_0 + theta_1 + theta_2);
//     J_s(1, 1) = -link_1_length * cos(theta_0 + theta_1) - link_2_length * cos(
//                                                                               theta_0 + theta_1 + theta_2);
//     J_s(1, 2) = -link_2_length * cos(theta_0 + theta_1 + theta_2);

//     return J_s;
// }

// std::vector<float> soft_limit_torques(std::vector<float> joint_thetas)
// {
//     static constexpr float discouraging_stiffness = 0.175f;
//     float joint_0_d_t = -discouraging_stiffness * joint_0_soft_limits.over_limits(joint_thetas.at(0));
//     float joint_1_d_t = -discouraging_stiffness * joint_1_soft_limits.over_limits(joint_thetas.at(1));
//     // float joint_2_d_t = -discouraging_stiffness * joint_2_soft_limits.over_limits(joint_thetas.at(2));

//     return {joint_0_d_t, joint_1_d_t, 0.0f};
// }