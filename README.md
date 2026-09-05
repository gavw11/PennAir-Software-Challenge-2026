# Shape Segmenter - PennAir Software Challenge 2026

A ROS 2 package that segments shapes out of video frames and calculates their 3D centroid coordinates in real time. Built for the PennAir Software Challenge 2026.

The pipeline is split across two nodes: one streams video frames onto a topic, and a second subscribes to that topic, runs the segmentation algorithm, and publishes both the annotated video and the detected centroids to other topics.

---

## Table of Contents

- [Overview](#overview)
- [Tasks](#tasks)
- [Package Structure](#package-structure)
- [The Algorithm](#the-algorithm)
- [Dependencies](#dependencies)
- [Installation & Build](#installation--build)
- [Running the Package](#running-the-package)
- [License](#license)

---

## Overview

<img width="2838" height="602" alt="image" src="https://github.com/user-attachments/assets/50a4a8fb-e0d5-4d85-bace-bdec7bdd3f24" />

The video stream node reads a video file frame-by-frame using OpenCV and publishes each frame to `/camera/Image_raw`. The video processing node subscribes to that stream, runs the shape-segmentation and centroid algorithm on every frame, then publishes the annotated frame to `/camera/Image_processed` and a text description of each detected object's coordinates to `/coords`.

## Package Structure

```
shape_segmenter/
├── launch/
│   └── segmenter.launch.py       # Launches both nodes together
├── shape_segmenter/
│   ├── stream_node.py            # Publishes video frames
│   ├── processing_node.py        # Subscribes, runs alg(), publishes results
│   ├── alg.py                    # Core segmentation + centroid algorithm
│   └── assets/                   # Sample video used for testing
├── package.xml
├── setup.py
└── setup.cfg
```

## Tasks
**Part 1**

<img width="1438" height="806" alt="image" src="https://github.com/user-attachments/assets/a93e00d0-f591-43d5-99aa-f6a373291203" />

**Part 2**

https://github.com/user-attachments/assets/cd82e853-0e6d-4bec-89fb-27424c59b5a3

**Part 3 & 4**

https://github.com/user-attachments/assets/175b7740-9af3-47fa-ba06-f1f8129a68c8

## The Algorithm

The segmentation logic is processed in `alg.py`. For every  frame:

1. **Grayscale + Canny edge detection** — the frame is converted to grayscale and run through `cv2.Canny` to extract shape outlines.
<img width="2842" height="1634" alt="Screenshot 2026-09-05 181454" src="https://github.com/user-attachments/assets/21d7a4a0-b1e2-46db-9274-0ad81fbbc56a" />


2. **Dilation** — the edges are dilated with a 5×5 kernel to close small gaps so outlines form fully enclosed regions.
<img width="2858" height="1638" alt="Screenshot 2026-09-05 181518" src="https://github.com/user-attachments/assets/7d943dfe-029c-4909-b9a6-1f246cca2ba7" />


3. **Border padding** — a 4px constant border is added so shapes that touch the edge of the frame are still detected as closed contours.
<img width="2848" height="1632" alt="image" src="https://github.com/user-attachments/assets/84fe6b77-49c8-4a76-b02d-d0fc55df7734" />
   
4. **Contour detection & filtering** — `cv2.findContours` finds all closed regions; contours with area outside `[7000, 500000]` px² are discarded (too small = noise, too large = background).
5. **Centroid calculation** — for each valid contour, image moments (`cv2.moments`) give the pixel-space centroid `(c_u, c_v)`.
6. **3D coordinate estimation** — pixel coordinates are converted to real-world X/Y/Z using a pinhole camera model:
   - A known reference object (measured circle radius in pixels: `cir_rad_x = 101.5`, `cir_rad_y = 104.5`) combined with the camera's focal lengths (`f_x`, `f_y`, from the provided intrinsic matrix) is used to calculate the depth `Z` via similar triangles.
   - `X` and `Y` are then computed from the pixel centroid, `Z`, and the focal lengths.
<img width="2360" height="524" alt="IMG_0023" src="https://github.com/user-attachments/assets/9066b886-d740-48a2-bc97-e98b908ce1ca" />

7. **Annotation** — contours, centroid markers, and coordinate text are drawn directly onto the frame, which is then resized to 50% for easier viewing before being published.

**Design note:** an initial approach considered using a pretrained segmentation model (FastSAM) for faster, more general shape detection, but this was later disallowed. Thus, traditional CV techniques were used.

## Dependencies

- ROS 2 (developed/tested on Ubuntu via WSL — should work on any ROS 2 distro with `ament_python`)
- Python 3
- `rclpy`
- `sensor_msgs`
- `std_msgs`
- `cv_bridge`
- OpenCV (`opencv-python` or `python3-opencv`)
- `numpy`

Install the non-ROS Python dependencies if needed:

```bash
pip install opencv-python numpy
```

## Installation & Build

Clone into a ROS 2 workspace's `src` folder and build with `colcon`:

```bash
cd ~/ros2_ws/src
git clone https://github.com/gavw11/PennAir-Software-Challenge-2026.git
cp -r PennAir-Software-Challenge-2026/shape_segmenter .

cd ~/ros2_ws
colcon build --packages-select shape_segmenter
source install/setup.bash
```

## Running the Package

### Option 1 — Launch file (recommended)

Starts both nodes together:

```bash
ros2 launch shape_segmenter segmenter.launch.py
```

### Option 2 — Run nodes individually

```bash
# Terminal 1
ros2 run shape_segmenter stream_node

# Terminal 2
ros2 run shape_segmenter processing_node
```

### Verifying it's working

```bash
# Watch the coordinate stream
ros2 topic echo /coords

# View the processed video topic
ros2 run rqt_image_view rqt_image_view
# then select /camera/image_processed from the dropdown
```

A live OpenCV window titled **"Processed Output (Algorithm)"** will also pop up directly from `processing_node`.

## License

Apache-2.0 — see `LICENSE`.
