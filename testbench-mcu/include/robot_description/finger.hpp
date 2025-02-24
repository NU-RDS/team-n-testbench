#pragma once
#include <math.h>
#include <vector>
#include <cmath>

#include "utils/angles.hpp"
#include "utils/helpers.hpp"
#include "utils/matrix.hpp"

/// @brief Torque limit in N-m
static constexpr float motor_torque_limit = 0.02f; // N*m

/// @brief Zeroing torque limit in N-m
static constexpr float zeroing_motor_torque_limit = 0.01f; // N*m

/// @brief Software spring stiffness
static constexpr float discouraging_stiffness = 0.01f; 

/// @brief PD gains
const auto kp = 0.17;
const auto kd = 0.002;

/// @brief Link 0 length in m
static constexpr float link_0_length = 44.165e-03; // m
/// @brief Link 1 length in m
static constexpr float link_1_length = 51.208e-03;

/// @brief Important radii
static constexpr float r_motor = 0.005; // 10 mm diameter shaft of otor
static constexpr float r_idler = 0.01; // 20 mm diameter idler pulley
static constexpr float r_pulley = 0.01; // 20 mm diameter pulley

/// @note The transmission ratio of joint : motor 
static constexpr float t1 = r_motor / r_pulley;
static constexpr float t2 = -r_motor / r_idler;
static constexpr float t3 = r_motor / r_pulley;
// [  t1  0  ]
// [  t2  t3 ]

/// @note The inverse of the transmission martrix
static constexpr float denom = 1 / (t1 * t3);
static constexpr float it1 = t1 / denom;
static constexpr float it2 = - t2 / denom;
static constexpr float it3 = t3 / denom;
// [ it3  it2 ]
// [  0   it1 ]



/// @brief Joint 0 limits in radians
static constexpr Limits<float> joint_0_limits = convert_angular_units(
    {-90.0, 90.0},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);
/// @brief Joint 1 limits in radians
static constexpr Limits<float> joint_1_limits = convert_angular_units(
    {-113.5, 99.5},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);

/// @brief Joint 0 soft limits in radians
static constexpr Limits<float> joint_0_soft_limits = convert_angular_units(
    {-70.0, 70.0},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);
/// @brief Joint 1 soft limits in radians
static constexpr Limits<float> joint_1_soft_limits = convert_angular_units(
    {-95.0, 80.0},
    AngleUnits::DEGREES,
    AngleUnits::RADIANS);

/// @brief Joint 0 calibration offset angles (calculated on startup)
static constexpr float joint_0_cali_offset = convert_angular_units(
    0.0, AngleUnits::DEGREES,
    AngleUnits::RADIANS);
/// @brief Joint 1 calibration offset angles (calculated on startup)
static constexpr float joint_1_cali_offset = convert_angular_units(
    0.0, AngleUnits::DEGREES,
    AngleUnits::RADIANS);

/// @brief Joint 0 velocity limits
static constexpr Limits<float> joint_0_vel_limits{-10.0, 10.0}; // m/s
/// @brief Joint 1 velocity limits
static constexpr Limits<float> joint_1_vel_limits{-10.0, 10.0};

/// @brief Performs forward kinematics for the finger.
/// @param joint_angles {theta_0, theta_1} in radians for the joints.
/// @returns {x, y, z} of the end effector.
static std::vector<float> forward_kinematics(std::vector<float> joint_angles)
{
    const float theta_0 = joint_angles.at(0);
    const float theta_1 = joint_angles.at(1);

    const float xe = link_0_length * cos(theta_0) + 
                     link_1_length * cos(theta_0 + theta_1);
    const float ze = link_0_length * sin(theta_0) +
                     link_1_length * sin(theta_0 + theta_1); 

    return {xe, 0.0, ze};
}

/// @brief Performs inverse kinematics
/// @param pos {x, y, z} in meters of the end effector.
/// @returns {theta_0, theta_1} of the joints in radians required to move to the location.
static std::vector<float> inverse_kinematics(std::vector<float> pos)
{
    // Check joint space of robot
    const float radius2 = pos.at(0) * pos.at(0) + pos.at(2) * pos.at(2); // radius squared
    const float radius = std::sqrt(radius2); // radius of finger
    if ((radius > link_0_length + link_1_length) || (radius < link_0_length - link_1_length)) {
        // invalid ik - outside of joint space
        return {std::nanf(""), std::nanf("")};
    }

    // Calculate relevant angles
    const float gamma = std::atan2(pos.at(2), pos.at(0));
    const float alpha = std::acos((radius2 + link_0_length * link_0_length - link_1_length * link_1_length) /
                                 (2 * radius * link_0_length));
    const float beta = std::acos((link_0_length * link_0_length + link_1_length * link_1_length - radius2) /
                                (2 * link_0_length * link_1_length));
    
    // Calculate desired theta values
    const float theta_0_1 = gamma - alpha; // theta 0, solution 1
    const float theta_0_2 = gamma + alpha; // theta 0, solution 2
    const float theta_1_1 = M_PI - beta; // theta 1, solution 1
    const float theta_1_2 = beta - M_PI; // theta 1, solution 2

    // Check validity of theta angles
    bool solution_1 = false;
    bool solution_2 = false;
    if ((joint_0_limits.over_limits(theta_0_1) == 0.0) and (joint_1_limits.over_limits(theta_1_1) == 0.0)) {
        solution_1 = true;
    } 
    if ((joint_0_limits.over_limits(theta_0_2) == 0.0) and (joint_1_limits.over_limits(theta_1_2) == 0.0)) {
        solution_2 = true;
    } 

    // If two available, prefer normal bending motion
    if (solution_1 and solution_2) {
        // Prefer theta_2 < 0
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

    return {std::nanf(""), std::nanf("")}; 

}