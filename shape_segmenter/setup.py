from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'shape_segmenter'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gavin',
    maintainer_email='gavwong@engineering.upenn.edu',
    description='Segments shapes + calculates their centroids',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'stream_node = shape_segmenter.stream_node:main',
            'processing_node = shape_segmenter.processing_node:main',
        ],
    },
)
