"""
Script Name: [DataPrep_ConvertYoloToCoco_AP_1.0.py]
Description: Script that converts yolo .txt files to COCO JSON format for all images in the dataset.
Created Date: YYYY-MM-DD
Author: Ana Petrovic 
Version: 1.0
Last Modified: 2024-04-12
Modified by: 

Example Usage:
python DataPrep_ConvertYoloToCoco_AP_1.0.py --path/to/images/folder --path/to/json/file --path/to/yolo/folder/segmentation --path/to/yolo/folder/detection

Dependencies:
os, json, PIL, datetime, cv2, numpy, argparse
"""
import os
import json
from PIL import Image
import datetime
import cv2
import numpy as np
import argparse
 
# Define parser
parser = argparse.ArgumentParser(description='Parse input, outputh, yolo det and yolo seg paths')

# Add arguments for folder paths
parser.add_argument('input_path', type=str, help='Path to the input path')
parser.add_argument('output_path', type=str, help='Path to the output path')
parser.add_argument('yolo_path_seg', type=str, help='Path to the yolo path seg')
parser.add_argument('yolo_path_det', type=str, help='Path to the yolo path det')

# Parse command-line arguments
args = parser.parse_args()

# Access the folder paths provided as arguments
input_path = args.input_path
output_path = args.output_path
yolo_path_seg = args.yolo_path_seg
yolo_path_det = args.yolo_path_det
 
# Define categories for the COCO dataset
categories = [
    {"id": 0, "name": "e"},
    {"id": 1, "name": "n"},
    {"id": 2, "name": "ne"},
    {"id": 3, "name": "nw"},
    {"id": 4, "name": "s"},
    {"id": 5, "name": "se"},
    {"id": 6, "name": "Sw"},
    {"id": 7, "name": "w"},
    {"id": 8, "name": "flat"},
]
 
# Define COCO dataset dictionary
coco_dataset = {
    "info": {
        "year": 2023,
        "version": "1.0",
        "description": "PlanetSoft rooftops segments dataset",
        "contributor": "Label Studio",
        "url": "",
        "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        },
    "images": [],
    "annotations": [],
    "categories": categories,
}
 
# Convert YOLO seg format to COCO JSON for image_id = 96
def convert_yolo_segmentation_to_coco(input_path, output_path):
    image_id = 0
   
    # Extract width and height
    for file_name in os.listdir(input_path):
        if file_name.endswith('.png'):
            image_path = os.path.join(input_path, file_name)
            image = Image.open(image_path)
            width, height = image.size
   
            # Create image dictionary
            image_dict = {
                    "width": width,
                    "height": height,
                    "id": image_id, 
                    "file_name": file_name,
            }
   
            # Add the image info to the COCO dataset
            coco_dataset["images"].append(image_dict) 
   
    #print(coco_dataset)
   
    # Load .txt files and read them line by line
            yolo_seg_name = file_name.replace('.png', '.txt') 
            yolo_seg_path = os.path.join(yolo_path_seg, yolo_seg_name) 
   
            if os.path.exists(yolo_seg_path): 
                with open(yolo_seg_path, 'r') as file:
                    
                    # print(file)
                    
                    # Returns a list, where the end of each line is marked with \n
                    lines = file.readlines()
                    
                    # print('lines before', lines)

                    # Delete \n
                    new_lines = []
                    new_lines_numbers = []
                    for line in lines:
                        new_lines.append(line.replace('\n', ''))

                    # print('lines after', new_lines)
                    # print('len ', len(new_lines))

                    # Convert strings to numbers
                    for line in new_lines:
                        parts = line.split()
                        new_lines = [int(parts[0])] + [float(x) for x in parts[1:]] # parts[0] represents category_id, and parts[1:] are segmentantion_points
                        new_lines_numbers.append(new_lines)
                    
                    # print('new lines numbers', new_lines_numbers)

                    # Iterate through new_lines_numbers, and for the current list extract category_id and segmentation_points,
                    for line in new_lines_numbers:
                        category_id = line[0]
                        segmentation_points = line[1:]

                        # Normalize segmentation points
                        segmentation_points_norm = []
                        segmentation_points_norm = [x * width if i % 2 == 0 else x * height for i, x in enumerate(segmentation_points)]

                        # Calculate area based on given segmentation points
                        contour = np.array(segmentation_points_norm, dtype=np.float32).reshape(-1, 2)
                        # print('shape of contour is ', contour)
                        area = cv2.contourArea(contour)
                        # print('area size ', area)

                        # Add values to corresponding keys
                        annotations_dict = { 
                            "id" : len(coco_dataset["annotations"]),
                            "image_id" : len(coco_dataset["images"]) - 1,
                            "category_id" : category_id,
                            "segmentation" : [segmentation_points_norm],
                            "bbox" : [],
                            "ignore" : 0,
                            "iscrowd" : 0,
                            "area" : area
                        }

                        coco_dataset["annotations"].append(annotations_dict)

                        # print('category id', category_id)
                        # print('segmentation points', segmentation_points)
                        # print('segmentation points norm', segmentation_points_norm)

                    image_id += 1

    # Save JSON
    with open(os.path.join(output_path, 'test-multi-image.json'), 'w') as file:
        json.dump(coco_dataset, file)
       
convert_yolo_segmentation_to_coco(input_path, output_path)