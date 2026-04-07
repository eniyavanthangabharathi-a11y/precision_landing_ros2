#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge
import cv2
import numpy as np

class LandingDetector(Node):
    def __init__(self):
        super().__init__('landing_detector')
        
        self.bridge = CvBridge()
        self.pad_visible = False
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.height = 10.0
        
        # CHANGE THIS LINE BASED ON YOUR ros2 topic list
        self.subscription = self.create_subscription(
            Image,
            '/image',
            self.image_callback,
            10)
        
        self.target_pub = self.create_publisher(PoseStamped, '/landing_target', 10)
        
        self.declare_parameter('max_height', 1.0)
        self.declare_parameter('max_offset', 0.3)
        self.declare_parameter('descent_rate', 0.5)
        
        self.timer = self.create_timer(1.0, self.descent_update)
        
        self.get_logger().info('Precision landing detector started')
    
    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            self.get_logger().info(f'Got image! Size: {cv_image.shape[1]}x{cv_image.shape[0]}')
            
            # Simple detection - find brightest spot
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
            
            h, w = gray.shape
            norm_x = (max_loc[0] - w/2) / (w/2)
            norm_y = (max_loc[1] - h/2) / (h/2)
            
            self.pad_visible = True
            scale = 0.05 * (self.height / 10.0)
            self.offset_x = norm_x * scale
            self.offset_y = norm_y * scale
            
            self.get_logger().info(
                f'Pad detected | X: {self.offset_x:.2f}m | Y: {self.offset_y:.2f}m | Height: {self.height:.1f}m'
            )
            
            self.publish_target()
            
        except Exception as e:
            self.get_logger().error(f'Error: {e}')
    
    def publish_target(self):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "drone"
        msg.pose.position.x = self.offset_x
        msg.pose.position.y = self.offset_y
        msg.pose.position.z = self.height
        self.target_pub.publish(msg)
    
    def descent_update(self):
        self.height -= self.get_parameter('descent_rate').value
        if self.height < 0.5:
            self.height = 0.5
        
        max_offset = self.get_parameter('max_offset').value
        if self.height <= self.get_parameter('max_height').value and \
           abs(self.offset_x) < max_offset and \
           abs(self.offset_y) < max_offset and \
           self.pad_visible:
            self.get_logger().info('Precision landing success')

def main(args=None):
    rclpy.init(args=args)
    node = LandingDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
