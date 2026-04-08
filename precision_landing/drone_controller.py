#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from px4_msgs.msg import TrajectorySetpoint
from px4_msgs.msg import OffboardControlMode

class DroneController(Node):
    def __init__(self):
        super().__init__('drone_controller')
        
        self.subscription = self.create_subscription(
            PoseStamped,
            '/landing_target',
            self.target_callback,
            10)
        
        self.trajectory_pub = self.create_publisher(
            TrajectorySetpoint,
            '/fmu/in/trajectory_setpoint',
            10)
        
        self.offboard_pub = self.create_publisher(
            OffboardControlMode,
            '/fmu/in/offboard_control_mode',
            10)
        
        self.timer = self.create_timer(0.05, self.publish_offboard_mode)
        self.get_logger().info('Drone controller started - waiting for landing target')
    
    def publish_offboard_mode(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        self.offboard_pub.publish(msg)
    
    def target_callback(self, msg):
        setpoint = TrajectorySetpoint()
        setpoint.position = [msg.pose.position.x, msg.pose.position.y, -msg.pose.position.z]
        setpoint.yaw = 0.0
        self.trajectory_pub.publish(setpoint)
        self.get_logger().info(f'Command: X={msg.pose.position.x:.2f}, Y={msg.pose.position.y:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = DroneController()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
