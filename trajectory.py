""" Generates a CSV file containing joint angles for a given trajectory
"""

from enum import auto, Enum
import math
import numpy as np
import matplotlib.pyplot as plt
import csv

class State(Enum):
    """Desired trajectory"""

    INITIALIZING = auto(),
    CIRCLE = auto(),
    TAPPING = auto(),

class MovingFinger():
    """Generates the joint angles."""

    def __init__(self, max_waypoints=20, run_state=State.INITIALIZING, radius=0.005, circle_origin=[0.08, 0, -0.002], z_start=0.0, z_end=-0.005):
        self.l0_len = 44.165e-03 # meters
        self.l1_len = 51.208e-03 
        self.j0_limits = (math.radians(-90.0), math.radians(90.0))
        self.j1_limits = (math.radians(-113.5), math.radians(99.5))
        self.state = run_state
        self.waypoints = []
        self.thetas = []
        self.num_waypoints = max_waypoints
        self.origin = circle_origin
        self.path_radius = radius
        self.x_tap = 0.08
        self.start_z = z_start
        self.end_z = z_end 

    def check_limits(self, theta, limit):
        if theta > limit[1]:
            return False
        elif theta < limit[0]:
            return False
        
        return True

    def adjust_angle(self, theta):
        if theta > math.pi:
            theta -= 2 * math.pi
        if theta < -math.pi:
            theta += 2 * math.pi
        return theta

    def forward_kinematics(self, joint_angles):
        theta0 = joint_angles[0]
        theta1 = joint_angles[1]

        xe = self.l0_len * math.cos(theta0) + self.l1_len * math.cos(theta0 + theta1)
        ze = self.l0_len * math.sin(theta0) + self.l1_len * math.sin(theta0 + theta1)

        return (xe, 0.0, ze)

    def inverse_kinematics(self, pos):
        xe = pos[0]
        ze = pos[2]
        radius_sq = xe**2 + ze**2 # radius squared
        radius = math.sqrt(radius_sq)

        if (radius > self.l0_len + self.l1_len or radius < abs(self.l0_len - self.l1_len)):
            return None  # invalid IK

        # Calculate relevant angles
        gamma = math.atan2(ze, xe)
        alpha = math.acos((radius_sq + self.l0_len**2 - self.l1_len**2) / (2 * radius * self.l0_len))
        beta = math.acos((self.l0_len**2 + self.l1_len**2 - radius_sq) / (2 * self.l0_len * self.l1_len))

        theta0_1 = self.adjust_angle(gamma - alpha)
        theta0_2 = self.adjust_angle(gamma + alpha)
        theta1_1 = self.adjust_angle(math.pi - beta)
        theta1_2 = self.adjust_angle(math.pi + beta)

        # Check valid joints and return
        if (math.degrees(theta1_1) < 0.0):
            if (self.check_limits(theta0_1, self.j0_limits) and self.check_limits(theta1_1, self.j1_limits)):
                print(f"first solution - theta 0: {math.degrees(theta0_1)}, theta 1: {math.degrees(theta1_1)}")
                return (theta0_1, theta1_1)
        elif (self.check_limits(theta0_2, self.j0_limits) and self.check_limits(theta1_2, self.j1_limits)):
            print(f"second solution - theta 0: {math.degrees(theta0_2)}, theta 1: {math.degrees(theta1_2)}")
            return (theta0_2, theta1_2)
        elif (self.check_limits(theta0_1, self.j0_limits) and self.check_limits(theta1_1, self.j1_limits)):
            print(f"first solution - theta 0: {math.degrees(theta0_1)}, theta 1: {math.degrees(theta1_1)}")
            return (theta0_1, theta1_1)
        return None

    def generate_trajectory(self):
        if self.state == State.CIRCLE:
            # Generate points to hit
            angle_step = 2 * math.pi / self.num_waypoints

            for i in range(self.num_waypoints):
                angle = i * angle_step

                # Calculate x and z position for each waypoint
                x = self.origin[0] + self.path_radius * math.cos(angle)
                z = self.origin[2] + self.path_radius * math.sin(angle)
                self.waypoints.append([x, 0.0, z])
                self.thetas.append(self.inverse_kinematics([x, 0.0, z]))

        elif self.state == State.TAPPING:
            # Generate points to hit
            z_step = (self.start_z - self.end_z) / self.num_waypoints

            for i in range(self.num_waypoints):
                z_inc = i * z_step
                x = self.x_tap
                z = self.start_z - z_inc

                self.waypoints.append([x, 0.0, z])
                self.thetas.append(self.inverse_kinematics([x, 0.0, z]))

    def generate_csv(self):
        # Write the waypoints to a CSV file
        with open('trajectory.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write a header row
            writer.writerow(['theta0', 'theta1', 'valid? (1 = True)'])
            # Write each waypoint as a row in the CSV file
            for waypoint in self.waypoints:
                thetas = self.inverse_kinematics([waypoint[0], 0.0, waypoint[2]])
                if thetas is not None:
                    writer.writerow([thetas[0], thetas[1], 1])
                else:
                    writer.writerow(['fail', 'fail', 0])
        print("Trajectory CSV file generated with", len(self.waypoints), "waypoints.")

def main(args=None):
    # Example for calling tapping
    finger = MovingFinger(run_state=State.TAPPING, max_waypoints=20)
    finger.generate_trajectory()
    finger.generate_csv()

if __name__ == '__main__':
    main()