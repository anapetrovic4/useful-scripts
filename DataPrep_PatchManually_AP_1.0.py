"""
Script Name: DataPrep_MergeClassesYolo_AP_1.0.py
Description: A script that patches image manually.
Created Date: 2024-04-12
Author: Ana Petrovic
Version: 1.0
Last Modified: 2024-04-12
Modified by: 

Example Usage:
python DataPrep_PatchManually_AP_1.0.py --path/to/image --path/to/output/dir

Dependencies:
PIL, os, argparse
"""
from PIL import Image
import os
import argparse

# Define parser
parser = argparse.ArgumentParser(description='Parse input and output paths')

# Add arguments for folder paths
parser.add_argument('input_path', type=str, help='Path to the original image that needs to be patched')
parser.add_argument('output_path', type=str, help='Path to the output path of patched images')

# Parse command-line arguments
args = parser.parse_args()

# Access the folder paths provided as arguments
input_path = args.input_path
output_path = args.output_path

# Define patch size and overlap
patch_size = 512
overlap = 2

def patch_image_with_overlaps(input_path, patch_size, overlap, output_path):

    with Image.open(input_path) as img:
            width, height = img.size

            for y in range(0, height, patch_size - overlap):
                for x in range(0, width, patch_size - overlap):
                
                    # Calculate the coordinates for slicing the patch
                    left = max(x, 0)
                    top = max(y, 0)
                    right = min(x + patch_size, width)
                    bottom = min(y + patch_size, height)

                    # Slice the patch
                    patch = img.crop((left, top, right, bottom))
                    
                    # Resize the patch to ensure it's exactly patch_size x patch_size
                    patch = patch.resize((patch_size, patch_size))
                    
                    # Save the patch
                    patch_filename = f"patch_{y}_{x}.jpg"
                    patch.save(os.path.join(output_path, patch_filename))
                    print(f"Patch saved: {patch_filename}")

patch_image_with_overlaps(input_path, patch_size, overlap, output_path)               
                