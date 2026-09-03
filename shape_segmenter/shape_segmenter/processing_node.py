#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import cv2
from cv_bridge import CvBridge
from shape_segmenter.alg import alg

class ImageProcessor(Node):
    def __init__(self):
        super().__init__('image_processing_node')
        
        #Create subscription to get raw video frames
        self.subscription = self.create_subscription(
            Image,
            'camera/image_raw',
            self.listener_callback,
            10)
        
        #Create publisher to send the processed frames out
        self.image_publisher = self.create_publisher(
            Image, 
            'camera/image_processed', 
            10)

        #Create publisher to send coords out
        self.coord_publisher = self.create_publisher(
            String,
            'coords',
            10
        )    
        
        self.bridge = CvBridge()
        self.get_logger().info('Image Processing Node with Publisher has started.')

    def listener_callback(self, img):
        #Convert the incoming ROS Image message to an OpenCV BGR image
        frame = self.bridge.imgmsg_to_cv2(img, desired_encoding='bgr8')
        
        #Apply centroid + image segmentation algorithm
        coords, processed_frame = alg(frame)
        
        #Convert the processed OpenCV frame back into a ROS Image message
        processed_img = self.bridge.cv2_to_imgmsg(processed_frame, encoding="bgr8")
        
        #Copy the original message header (keeps timestamps synchronized)
        processed_img.header = img.header
        
        #Publish processed image to topic
        self.image_publisher.publish(processed_img)

        i = 0
        for coord in coords:
            #Send coords to topic
            coord_msg = String()
            coord_msg.data = f"Object {i}: X: {coord[0]}, Y: {coord[1]}, Z: {coord[2]}"
            self.coord_publisher.publish(coord_msg)
            i+=1

        #Show processed frame
        cv2.imshow("Processed Output (Algorithm)", processed_frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ImageProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
