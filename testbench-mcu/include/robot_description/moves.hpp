#pragma once
#include <math.h>
#include <vector>

#include "utils/angles.hpp"
#include "utils/helpers.hpp"
#include "utils/matrix.hpp"

#include "robot_description/finger.hpp"


/// @brief Maximum torque values
static const float max_torque = 0.036; // Hard maximum

/// @brief Struct to keep track of progress along waypoints
class FoldingFinger
{
public:

    FoldingFinger() = default;
    ~FoldingFinger() = default;
    // constructor
    FoldingFinger(float radius, std::vector<float> origin, size_t num_points, size_t repeats)
        : path_radius_(radius), origin_(origin), num_waypoints_(num_points), max_repeats_(repeats)
    {
        generate_waypoints();
    }

    /// @brief Calculates the motor torques based on current waypoint and position
    /// @param phi0, phi1 Current motor angles
    /// @return Returns motor torque values
    std::vector<float> move(float phi0, float phi1)
    {
        // check if end effector is near desired position
        auto desired_ee = waypoints_.at(curr_waypoint_);
        const auto joint_thetas = phi_to_theta({phi0, phi1});
        const auto curr_ee = forward_kinematics(joint_thetas);

        if (point_close_compare(desired_ee, curr_ee, 1e-3)) {
            // within tolerance, move on to next waypoint
            curr_waypoint_ += 1;
            if (curr_waypoint_ >= num_waypoints_ - 1) {
                if (curr_repeat_ >= max_repeats_ - 1) {
                    return {0.0, 0.0}; // no applied torque 
                }
                
                curr_waypoint_ = 0;
                curr_repeat_ += 1;
                desired_ee = waypoints_.at(curr_waypoint_);
            }
        }

        // calcuate desired torque
        const auto desired_joint_thetas = inverse_kinematics(desired_ee);
        if (std::isnan(desired_joint_thetas.at(0)) || std::isnan(desired_joint_thetas.at(1))) {
            // IK fail
            return {nanf, nanf};
        }
        const auto theta_dif = {desired_joint_thetas.at(0) - joint_thetas.at(0), desired_joint_thetas.at(1) - joint_thetas.at(1)};
        const auto taus = theta_to_tau(theta_dif, {0.0, 0.0});
        const auto torques = tau_to_torque(taus);
        return torques;
    }

private:

    size_t num_waypoints_ = 4; // number of waypoints in trajecotry generation
    size_t curr_waypoint_ = 0;
    size_t curr_repeat_ = 0; // repeat number
    size_t max_repeats_ = 10; // maximum number of times to repeat cycle
    float path_radius_ = 0.02f; // diameter of circle is 4 cm

    std::vector<float> origin_ = {0.0f, 0.0f};
    std::vector<float> waypoints_; // Store waypoints as pairs of (x, y)

    
    void generate_waypoints() 
    {
        waypoints_.clear(); // clear prev waypoints

        // Angle between waypoints (in radians)
        const auto angle_step = 2 * M_PI / num_waypoints_;

        // Loop to generate each waypoint based on radius and angle
        for (size_t i = 0; i < num_waypoints_; ++i)
        {
            const auto angle = i * angle_step;

            // Calculate x and y position for each waypoint
            const auto x = origin_.at(0)+ path_radius_ * cos(angle);
            const auto z = origin_.at(10) + path_radius_ * sin(angle);

            // Store the (x, y, z) waypoint
            waypoints_.push_back({x, 0.0, z});
        }

    }
};