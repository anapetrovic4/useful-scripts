"""
Script Name: DataPrep_PatchWithPatchify_AP_1.0.py
Description: A script that patches image using patchify library and creates corresponding masks.
Created Date: 2024-04-12
Author: Ana Petrovic
Version: 1.0
Last Modified: 2024-04-12
Modified by: 

Example Usage:
python DataPrep_PatchWithPatchify_AP_1.0.py --path/to/image --path/to/output/dir

Dependencies:
patchify, cv2, os
"""
from patchify import patchify
import cv2
import os

# Read images and labels directories
images_path = 'path/to/images/folder'
masks_path = 'path/to/masks/folder'

counter = 0

# Patchify images 
for filename in os.listdir(images_path):
    img_path = os.path.join(images_path, filename)
    img = cv2.imread(img_path,cv2.COLOR_BGR2RGB)
   
    if img.shape[0] >= 2640 and img.shape[1] >= 1978:
       # Define patch size
       patch_width = img.shape[1] // 2  # Divide width by 2
       patch_height = img.shape[0] // 2  # Divide height by 2

       patches_img = patchify(img, (patch_height, patch_width, 3), step=(patch_height, patch_width, 3))

       for i in range(patches_img.shape[0]):
           for j in range(patches_img.shape[1]):
               single_patch_img = patches_img[i, j, 0, :, :, :]
               
               counter += 1
               
               patch_filename = f'image_{counter}_{i}_{j}.png'
               patch_save_path = os.path.join('path/to/output/folder', patch_filename)
               cv2.imwrite(patch_save_path, single_patch_img)
    else:
       print(f"Image '{filename}' is smaller than the desired patch size.")
       continue
   
print('Shape of single patch ', single_patch_img.shape)
# Reset counter
counter = 0

# Patchify labels 
for filename in os.listdir(masks_path):
    msk_path = os.path.join(masks_path, filename)
    msk = cv2.imread(msk_path,cv2.IMREAD_GRAYSCALE)
    
    patches_msk = patchify(msk, (patch_height, patch_width), step=256)
    
    for i in range(patches_msk.shape[0]):
        for j in range(patches_msk.shape[1]):
            single_patch_msk = patches_msk[i, j, :, :]
                    
            counter += 1
                    
            patch_filename = f'mask_{counter}_{i}_{j}.png'
            patch_save_path = os.path.join('path/to/labels', patch_filename)
            cv2.imwrite(patch_save_path, single_patch_msk)
print('Shape of single patch ', single_patch_msk.shape)
