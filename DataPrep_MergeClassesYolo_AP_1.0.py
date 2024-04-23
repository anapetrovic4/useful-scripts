"""
Script Name: DataPrep_MergeClassesYolo_AP_1.0.py
Description: A script that merges multiple classes under single class from yolo format.
Created Date: 2024-04-12
Author: Ana Petrovic
Version: 1.0
Last Modified: 2024-04-12
Modified by: 

Example Usage:
python DataPrep_MergeClassesYolo_AP_1.0.py

Dependencies:
os
"""
import os

def merge_classes(folder_path):
    unique_chars = {}
    files_first_appearance = {}

    # Iterate through all files in the given folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            new_content = []
            with open(os.path.join(folder_path, filename), 'r') as file:
                for line in file:
                    if line:  # Check if line is not empty
                        first_char = line[0]
                        if first_char != '0':
                            new_line = '1' + line[1:]
                            new_content.append(new_line)
                        else:
                            new_content.append(line)
            
            # Write the updated content back to the file
            with open(os.path.join(folder_path, filename), 'w') as file:
                file.writelines(new_content)

    return "Merged classes successfully"

# Sample usage
folder_path = '/mnt/c/projects/ttpla-dataset-with-roboflow-anns/yolo/labels/val'
result = merge_classes(folder_path)
print(result)