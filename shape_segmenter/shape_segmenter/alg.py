#Import necessary modules
import cv2
import numpy as np

# Was told that segmentation model cannot be used unless it was trained
# Load model (in this case, FastSAM is used for fast computation for object segmentation)
# model = FastSAM('FastSAM-s.pt')



#---Values used for calculating 3D coordiantes---

#Measured pixel values
cir_rad_x = 101.5
cir_rad_y = 104.5

#Focal lengths from given intrinsic matrix
f_x = 2564.3186869
f_y = 2569.70273111

#Calculate the depth Z utilizing similar triangles & pinhole camera model
z_x = (10 / cir_rad_x) * f_x
z_y = (10 / cir_rad_y) * f_y
c_z = (z_x + z_y) / 2

#------------------------------------------------

#Create kernel for dilation
kernel = np.ones((5, 5), np.uint8)

def alg(frame):
        coords = []
        global c_z
        #Convert to grey scale & perform Canny Edge Detectino

        grey_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grey_img, threshold1=30, threshold2=50)

        #Dilate image to create enclosed areas that can be thought of as shapes
        dilated_image = cv2.dilate(edges, kernel, iterations=1)

        #Add padding around border to allow shapes on edge of screen to be segmented
        pad = 4
        padded = cv2.copyMakeBorder(
            dilated_image, 
            top=pad, bottom=pad, left=pad, right=pad, 
            borderType=cv2.BORDER_CONSTANT, 
            value=[255]
        )

        #Find contours to calculate areas used for filtering, segmentation, and centroid calculations
        contours, _ = cv2.findContours(padded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            cnt = cnt - np.array([pad, pad])  # undo the padding offset once, here
            area = cv2.contourArea(cnt)

            #Filter out noisy shapes
            if (area > 7000) and (area < 500000):

                #Draw contours
                cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)

                #Use OpenCV moments to calculate centroids
                M = cv2.moments(cnt) 
                if M["m00"] != 0:
                    #Get pixel coordinates of centroid
                    c_u = int(M["m10"] / M["m00"])
                    c_v = int(M["m01"] / M["m00"])
                            
                    cv2.circle(frame, (c_u, c_v), 5, (0, 255, 0), -1)

                    #Calculate x & y coordinates utilizing the intrinsic matrix, z, and pixel coordinates
                    c_x = c_u / f_x * c_z
                    c_y = c_v / f_y * c_z
                    
                    #Truncate values to 2 decimal places
                    c_x = int(c_x * 100) / 100
                    c_y = int(c_y * 100) / 100
                    c_z = int(c_z * 100) / 100

                    coords.append([c_x, c_y, c_z])

                    #Write coordinates
                    cen_text = f"[Centroid: ({c_x}, {c_y}, {c_z})]"
                    cv2.putText(frame, cen_text, (int(c_u-250), int(c_v+50)), cv2.FONT_HERSHEY_PLAIN, fontScale=2, color=(255, 255, 255), thickness=3)

        #Resize frame for easier viewing
        frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
        return coords, frame

