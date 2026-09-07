from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    stream_node = Node(
        package='shape_segmenter',     # The ROS 2 package containing the executable
        executable='stream_node',           # The name of the built executable
        name='streamer_node',
        parameters=[{'input_path': 'file:///home/gavin/ros2_ws/src/shape_segmenter/shape_segmenter/assets/Task 2.mp4'}],
    )

    processing_node = Node(
        package='shape_segmenter',
        executable='processing_node',
        name='video_processor',
    )

    # 2. Return the LaunchDescription populated with your nodes
    return LaunchDescription([
        stream_node,
        processing_node
    ])
