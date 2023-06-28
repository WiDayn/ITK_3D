import os

import fiftyone as fo
from fiftyone import Dataset

# The directory containing the source images
data_path = "./dataset"

# The path to the COCO labels JSON file
labels_path = "./coco_data.json"

# Import the dataset
dataset = fo.Dataset.from_dir(
    dataset_type=fo.types.COCODetectionDataset,
    data_path=data_path,
    labels_path=labels_path,
)

session = fo.launch_app()
session.dataset = dataset
session.wait()