"""
Script Name: DataPrep_DownsizeImages_AP_1.0.py
Description: A script that takes paths to original images, downsizes them to wanted size and then saves them in a new folder.
Created Date: YYYY-MM-DD
Author: Ana Petrovic
Version: 1.0
Last Modified: 2024-04-12
Modified by: Ana

Example Usage:
python DataPrep_DownsizeImages_AP_1.0.py --path/to/original/images --path/to/downsized/folder

Dependencies:
os, argparse, PIL
"""

import os
import argparse
from PIL import Image

# Define parser
parser = argparse.ArgumentParser(description='Paths to images and annotations')

# Add arguments for folder paths
parser.add_argument('original_images', type=str, help='Path to original images')
parser.add_argument('downsized_images', type=str, help='Path to downsized images')

# Parse command-line arguments
args = parser.parse_args()

# Access the folder paths provided as arguments
original_images = args.original_images
downsized_images = args.downsized_images

# Set the new size of images
NEW_SIZE = (512, 512)

# Load images from original_images file, resize and save them in a new folder
list_original_images = os.listdir(original_images)

for img in list_original_images:
        img_path = os.path.join(original_images, img)
        image = Image.open(img_path)
        downsized_image = image.resize(NEW_SIZE)
        downsized_images_path = os.path.join(downsized_images, img)
        downsized_image.save(downsized_images_path)
    
