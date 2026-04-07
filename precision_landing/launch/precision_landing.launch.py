from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='precision_landing',
            executable='landing_detector',
            name='landing_detector',
            parameters=[{
                'max_height': 1.0,
                'max_offset': 0.3,
                'descent_rate': 0.5,
                'detection_rate': 0.8
            }]
        )
    ])
