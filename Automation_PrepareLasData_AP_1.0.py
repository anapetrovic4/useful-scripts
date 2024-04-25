"""
Script Name: Automation_PrepareLasData_AP_1.0.py
Description: Perform voxel downsampling on point clouds and labels, convert .pcd and .labels to .las format
Created Date: 2024-04-17
Author: Aleksandar Lukic, Ana Petrovic
Version: 1.0
Last Modified: 2024-04-25
Modified by: Ana Petrovic (Modified script to create multiple las files for each pcd file)

Example Usage:
python Automation_PrepareLasData_AP_1.0.py --path/to/dense/point/clouds --path/to/dense/labels --voxel size

***Note***: 
Voxel size refers to the size of voxel grid used for downsampling. 
Downsampling is performed by dividing a point cloud into smaller voxel grids
and then extracting a representative point (typically average point) 
from each grid to reduce the point cloud's density.

***Expected folder structure***:
.
├──Automation_PrepareLasData_AP_1.0.py
└── dataset
    ├── downsampled_data
    │   ├── path/to/your/downsampled/labels
    │   └── path/to/your/downsampled/pcd
    ├── las
    │   ├── path/to/output/las/with/labels 
    │   └── path/to/output/las
    └── raw_data
        ├── path/to/your/labels (optional)
        └── path/to/your/pcd

Dependencies:
open3d, os, numpy, laspy
"""
import open3d
import os
import numpy as np
import laspy

# Create paths to output las files
las_folder = os.listdir('/mnt/c/ems/Ana/AP_test/dataset/las')

# Read .labels and return array of integers which represent colors for semantic segmentation
def load_labels(label_path):

    # Assuming each line is a valid int
    with open(label_path, "r") as f:
        labels = [int(line) for line in f]
    print('shape of labels ', np.array(labels).shape)
    return np.array(labels, dtype=np.int32)

# Write downsampled labels in new file
def write_labels(label_path, labels):
    with open(label_path, "w") as f:
        for label in labels:
            f.write("%d\n" % label)

# Convert pcd to las
def convert_pcd_to_las(pcd_file, las_file_path):

    # Load PCD file
    pcd = pcd_file

    # Convert Open3D.o3d.geometry.PointCloud to numpy array
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors) if pcd.colors else None

    # Create a new LAS file
    header = laspy.LasHeader(point_format=2, version="1.2")
    las = laspy.LasData(header)

    # Populate LAS file with points from PCD
    las.x = points[:, 0]
    las.y = points[:, 1]
    las.z = points[:, 2]

    if colors is not None:

        # Normalize colors from [0, 1] to [0, 255] and assign to LAS
        las.red = (colors[:, 0] * 255).astype(np.uint16)
        las.green = (colors[:, 1] * 255).astype(np.uint16)
        las.blue = (colors[:, 2] * 255).astype(np.uint16)

    # Write LAS file to disk
    las.write(las_file_path)

# Convert labels to las with classification
def convert_pcd_to_las_with_classifications(pcd_file, las_file_path, classifications_path):
    
    # Load PCD file
    pcd = pcd_file

    # Convert Open3D.o3d.geometry.PointCloud to numpy array
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors) if pcd.colors else None

    # Load classifications
    with open(classifications_path, 'r') as file:
        classifications = np.array([int(line.strip()) for line in file.readlines()])

    # Create a new LAS file
    header = laspy.LasHeader(point_format=2, version="1.2")
    las = laspy.LasData(header)

    # Populate LAS file with points and classifications from PCD
    las.x = points[:, 0]
    las.y = points[:, 1]
    las.z = points[:, 2]
    
    # Print shapes of points and classifications before assignment
    print("Shape of points array:", points.shape)
    print("Shape of classifications array:", classifications.shape)
    
    las.classification = classifications

    if colors is not None:
        # Normalize colors from [0, 1] to [0, 255] and assign to LAS
        las.red = (colors[:, 0] * 255).astype(np.uint16)
        las.green = (colors[:, 1] * 255).astype(np.uint16)
        las.blue = (colors[:, 2] * 255).astype(np.uint16)

    # Write LAS file to disk
    las.write(las_file_path)

def down_sample( dense_pcd_path, dense_label_path, sparse_pcd_path, sparse_label_path, voxel_size):

    # Skip if done
    if os.path.isfile(sparse_pcd_path) and ( not os.path.isfile(dense_label_path) or os.path.isfile(sparse_label_path)):
        print("Skipped:", file_prefix)
        return
    else:
        print("Processing:", file_prefix)

    # Inputs
    dense_pcd = open3d.io.read_point_cloud(dense_pcd_path)
    try:
        dense_labels = load_labels(dense_label_path)
    except:
        dense_labels = None

    # Skip label 0, we use explicit frees to reduce memory usage
    print("Num points:", np.asarray(dense_pcd.points).shape[0])
    if dense_labels is not None:
        non_zero_indexes = dense_labels != 0

        dense_points = np.asarray(dense_pcd.points)[non_zero_indexes]
        dense_pcd.points = open3d.utility.Vector3dVector()
        dense_pcd.points = open3d.utility.Vector3dVector(dense_points)
        del dense_points

        dense_colors = np.asarray(dense_pcd.colors)[non_zero_indexes]
        dense_pcd.colors = open3d.utility.Vector3dVector()
        dense_pcd.colors = open3d.utility.Vector3dVector(dense_colors)
        del dense_colors

        dense_labels = dense_labels[non_zero_indexes]
        print("Num points after 0-skip:", np.asarray(dense_pcd.points).shape[0])

    # Downsample points
    min_bound = dense_pcd.get_min_bound() - voxel_size * 0.5
    max_bound = dense_pcd.get_max_bound() + voxel_size * 0.5

    sparse_pcd, cubics_ids, something = open3d.geometry.PointCloud.voxel_down_sample_and_trace( dense_pcd, voxel_size, min_bound, max_bound, approximate_class=False)
    
    print('Type od sparse_pcd ', type(sparse_pcd))
    print('Type od cubics ids ', type(cubics_ids))
    print('Type of something ', type(something))

    sparse_pcd_array = np.asarray(sparse_pcd.points)
    
    print('First 5 elements of sparse pcd array \n', sparse_pcd_array[:5])
    print('First 5 elements of cubics ids \n', cubics_ids[:5])
    print('First 5 elements of something \n', something[:5])
    print('Shape of cubics ids ', cubics_ids.shape)
    print('Data types of cubics ids ', cubics_ids.dtype)

    open3d.io.write_point_cloud(filename = sparse_pcd_path, pointcloud = sparse_pcd, format='auto', write_ascii=False, compressed=False, print_progress=False)
    print("Point cloud written to:", sparse_pcd_path)

    #convert_pcd_to_las(sparse_pcd, las) test
    #print('Successfully converted .pcd to .las to: ', las)

    # Downsample labels
    if dense_labels is not None:
        sparse_labels = []
        for cubic_ids in cubics_ids:
            cubic_ids = cubic_ids[cubic_ids != -1]
            cubic_labels = dense_labels[cubic_ids]
            sparse_labels.append(np.bincount(cubic_labels).argmax())
        
        sparse_labels = np.array(sparse_labels)

        write_labels(sparse_label_path, sparse_labels)
        print("Labels written to:", sparse_label_path)

        #convert_pcd_to_las_with_classifications(sparse_pcd, las_file_path=las_labels, classifications_path=sparse_label_path)
        #print('Successfully converted .labels to .las to: ', las_labels) test
        
if __name__ == "__main__":
    voxel_size = 0.05

    # By default
    # raw data: "dataset/semantic_raw"
    # downsampled data: "dataset/semantic_downsampled"
    current_dir = os.path.dirname(os.path.realpath(__file__))
    print('Current dir ', current_dir)
    dataset_dir = os.path.join(current_dir, "dataset")
    raw_dir = os.path.join(dataset_dir, "raw_data")
    downsampled_dir = os.path.join(dataset_dir, "downsampled_data")

    # Create downsampled_dir
    os.makedirs(downsampled_dir, exist_ok=True)

    files = os.listdir('/mnt/c/ems/Ana/AP_test/dataset/raw_data')
    list_labels = []
    list_pcds = []

    # Create las file with labels
    for file in files:
        if file.endswith('.labels'):
            list_labels.append(file)

            file_name = os.path.splitext(file)[0]

            las_labels = os.path.join('/mnt/c/ems/Ana/AP_test/dataset/las', file_name + '_labels' + '.las')
            with open(las_labels, 'w') as f:
                pass
    
    # Create las file
    for file in files:
        if file.endswith('.pcd'):
            list_pcds.append(file)

            file_name = os.path.splitext(file)[0]

            las = os.path.join('/mnt/c/ems/Ana/AP_test/dataset/las', file_name + '.las')
            with open(las, 'w') as f:
                pass

    # Iterate through list of pcd files and check if labels files are present
    for file in list_pcds:
        name, extension = os.path.splitext(file)
        file_prefix = name
        label_file = file_prefix + '.labels'

        # Set the path for las files test
        las_path = os.path.join('/mnt/c/ems/Ana/AP_test/dataset/las', file_prefix + '.las')
        las_labels_path = os.path.join('/mnt/c/ems/Ana/AP_test/dataset/las', file_prefix + '_labels.las')

        if label_file in list_labels:
            print('File ', file)
            dense_pcd_path = os.path.join(raw_dir, file_prefix + ".pcd")
            dense_label_path = os.path.join(raw_dir, file_prefix + ".labels")
            sparse_pcd_path = os.path.join(downsampled_dir, file_prefix + ".pcd")
            sparse_label_path = os.path.join(downsampled_dir, file_prefix + ".labels")
            down_sample(dense_pcd_path, dense_label_path, sparse_pcd_path, sparse_label_path, voxel_size)

            # Convert pcd to las with labels
            convert_pcd_to_las_with_classifications(open3d.io.read_point_cloud(sparse_pcd_path), las_labels_path, sparse_label_path)
        else:
            dense_pcd_path = os.path.join(raw_dir, file_prefix + ".pcd")
            sparse_pcd_path = os.path.join(downsampled_dir, file_prefix + ".pcd")
            down_sample(dense_pcd_path, None, sparse_pcd_path, None, voxel_size)

            # Convert pcd to las
            convert_pcd_to_las(open3d.io.read_point_cloud(sparse_pcd_path), las_path)
        