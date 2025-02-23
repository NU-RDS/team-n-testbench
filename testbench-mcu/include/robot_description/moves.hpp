#pragma once
#include <math.h>
#include <vector>

#include "utils/angles.hpp"
#include "utils/helpers.hpp"
#include "utils/matrix.hpp"

#include "robot_description/finger.hpp"
#include "com_manager/odrive_manager.hpp"

/// \brief The state of the system
enum FingerMotion : uint8_t
{
    CALIBRATION,
    CIRCULAR
};

/// @brief Maximum torque values
static const float max_torque = 0.036; // Hard maximum

/// @brief Struct to keep track of progress along waypoints
class MovingFinger
{
public:

    MovingFinger() = default;
    ~MovingFinger() = default;
    // constructor
    MovingFinger(
        ODriveManager<CAN2> &odrive0,
        ODriveManager<CAN3> &odrive1,
        float radius, 
        std::vector<float> origin, 
        size_t num_points, 
        size_t repeats)
        : odrive0_(odrive0),
          odrive1_(odrive1),
          path_radius_(radius), 
          origin_(origin), 
          num_waypoints_(num_points), 
          max_repeats_(repeats)
    {
        generate_waypoints();
    }

    /// @brief Change the state of the system to generate various waypoints
    /// @param state State to switch to
    void set_state(FingerMotion state) {
        finger_motion_ = state;
    }

    /// @brief Calculates the motor torques based on current waypoint and position
    /// @param phi0, phi1 Current motor angles
    /// @return Returns motor torque values
    std::vector<float> generate_torque_values(float phi0, float phi1)
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
                    // CHANGE STATE TO READY HERE
                }
                
                curr_waypoint_ = 0;
                curr_repeat_ += 1;
                desired_ee = waypoints_.at(curr_waypoint_);
            }
        }

        // calcuate desired torque
        const auto desired_joint_thetas = inverse_kinematics(desired_ee);
        if (std::isnan(desired_joint_thetas.at(0)) or std::isnan(desired_joint_thetas.at(1))) {
            // IK fail
            // CHANGE STATE TO ERROR HERE
            return {nanf, nanf};
        }
        std::vector<float> theta_dif = {desired_joint_thetas.at(0) - joint_thetas.at(0), desired_joint_thetas.at(1) - joint_thetas.at(1)};
        const auto taus = theta_to_tau(theta_dif, {0.0, 0.0});
        const auto torques = tau_to_torque(taus);
        return torques;
    }
    
    /// @brief Moves the first joint to a desired angle.
    /// @param theta_des desired angle of the first joint (rad).
    void move_j1(float theta_des) 
    {
        // Get position difference
        const auto phi_0 = odrive0_.odrive_user_data_.last_feedback.Pos_Estimate;
        const auto phi_1 = odrive1_.odrive_user_data_.last_feedback.Pos_Estimate; 
        const auto joint_thetas = motors_to_joints({phi_0, phi_1}); // TODO: ONCE WE CALIBRATE CHANGE FUNCTION TO PHI TO THETA
        const auto theta_0_dif = theta_des - joint_thetas.at(0);

        // Send joints and get motor torque
        const auto taus = theta_to_tau({theta_0_dif, 0.0}, {0.0, 0.0});
        const auto torques = tau_to_torque(taus);

        // Send torque
        const auto torque_0 = limit<float>(torques.at(0), max_torque);
        const auto torque_1 = limit<float>(torques.at(1), max_torque);
        odrive0_.odrive_.setTorque(torque_0);
        odrive1_.odrive_.setTorque(torque_1);
    }

    /// @brief Moves the second joint to a desired angle.
    /// @param theta_des desired angle of the second joint (rad).
    void move_j2(float theta_des) 
    {
        // Get position difference
        const auto phi_0 = odrive0_.odrive_user_data_.last_feedback.Pos_Estimate;
        const auto phi_1 = odrive1_.odrive_user_data_.last_feedback.Pos_Estimate; 
        const auto joint_thetas = motors_to_joints({phi_0, phi_1}); // TODO: ONCE WE CALIBRATE CHANGE FUNCTION TO PHI TO THETA
        const auto theta_1_dif = theta_des - joint_thetas.at(1);

        // Send joints and get motor torque
        const auto taus = theta_to_tau({0.0, theta_1_dif}, {0.0, 0.0});
        const auto torques = tau_to_torque(taus);

        // Send torque
        const auto torque_0 = limit<float>(torques.at(0), max_torque);
        const auto torque_1 = limit<float>(torques.at(1), max_torque);
        odrive0_.odrive_.setTorque(torque_0);
        odrive1_.odrive_.setTorque(torque_1);
    }

    /// @brief Creates class to move finger in a circle
    void move_circle() {
        // get current motor angles
        const auto phi_0 = odrive0_.odrive_user_data_.last_feedback.Pos_Estimate;
        const auto phi_1 = odrive1_.odrive_user_data_.last_feedback.Pos_Estimate; 

        // Call the move function and print the output torques
        std::vector<float> torques = generate_torque_values(phi_0, phi_1);
        if (std::isnan(torques.at(0)) || std::isnan(torques.at(1))) {
            // IK fail, not possible
            // CHANGE STATE TO ERROR
        }
        odrive0_.odrive_.setTorque(torques.at(0));
        odrive1_.odrive_.setTorque(torques.at(1));
    }

public:

    /// \brief Address of first odrive
    ODriveManager<CAN2> &odrive0_;

    /// \brief Address of second odrive
    ODriveManager<CAN3> &odrive1_;

    size_t num_waypoints_ = 4; // number of waypoints in trajecotry generation
    size_t curr_waypoint_ = 0;
    size_t curr_repeat_ = 0; // repeat number
    size_t max_repeats_ = 10; // maximum number of times to repeat cycle
    float path_radius_ = 0.02f; // diameter of circle is 4 cm

    std::vector<float> origin_ = {0.0f, 0.0f, 0.0f}; 
    std::vector<std::vector<float>> waypoints_; // Store waypoints as pairs of (x, y)

    FingerMotion finger_motion_ = FingerMotion::CALIBRATION;

    void generate_waypoints() 
    {
        waypoints_.clear(); // clear prev waypoints

        switch (finger_motion_)
        {
        case FingerMotion::CIRCULAR:

            // Angle between waypoints (in radians)
            const auto angle_step = 2 * M_PI / num_waypoints_;

            // Loop to generate each waypoint based on radius and angle
            for (size_t i = 0; i < num_waypoints_; ++i)
            {
                const auto angle = i * angle_step;

                // Calculate x and y position for each waypoint
                const auto x = origin_.at(0)+ path_radius_ * cos(angle);
                const auto z = origin_.at(2) + path_radius_ * sin(angle);

                // Store the (x, y, z) waypoint
                waypoints_.push_back({x, 0.0, z});
            }   
            break;
        
        default:
            break;
        }
    }
};