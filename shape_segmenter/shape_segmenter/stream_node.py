#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class VideoStreamer(Node):
    def __init__(self):
        super().__init__('video_streamer_node')

        self.declare_parameter('input_path', '/home/gavin/ros2_ws/src/shape_segmenter/shape_segmenter/assets/Task 3&4.mp4')
        input_path = self.get_parameter('input_path').value

        #Initialize video stream
        self.cap = cv2.VideoCapture(input_path, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            self.get_logger().error(f'Could not open video file at:')
            return

        #Get video fps so ROS can stream accurately
        video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0:
            video_fps = 30.0
            
        self.get_logger().info(f'Streaming at {video_fps} FPS')

        #Create publisher to send video frames
        self.publisher_ = self.create_publisher(Image, 'camera/image_raw', 10)
        self.timer = self.create_timer(1.0 / video_fps, self.timer_callback)
        self.bridge = CvBridge()

    def timer_callback(self):
        ret, frame = self.cap.read()
        
        if not ret:
            self.get_logger().info('End of video file. Rewinding to start.')
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher_.publish(img_msg)

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = VideoStreamer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
