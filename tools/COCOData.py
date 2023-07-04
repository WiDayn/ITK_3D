import json

# COCO数据集
class COCOData:
    def __init__(self):
        self.info = {
            "description": "Spine Key Points Data Set",
            "url": "https://KFC-CRAZY-THURSDAY-VME50.com",
            "version": "1.0",
            "year": 2023,
            "contributor": "ZengQiang",
            "date_created": "2023-06-26"
        }
        self.now_annotation_id = 0
        self.images = []
        self.categories = []
        self.annotations = []

    def add_image(self, image_id, width, height, file_name):
        image = {
            "id": image_id,
            "width": width,
            "height": height,
            "file_name": file_name
        }
        self.images.append(image)

    def add_category(self, category_id, name, supercategory, keypoints=None, skeleton=None):
        category = {
            "id": category_id,
            "name": name,
            "supercategory": supercategory
        }
        if keypoints is not None:
            category["keypoints"] = keypoints
        if skeleton is not None:
            category["skeleton"] = skeleton

        self.categories.append(category)

    def add_annotation_object(self, image_id, category_id, segmentation, area, num_keypoints, keypoints, bbox, iscrowd=0):
        annotation = {
            "id": self.now_annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "segmentation": segmentation,
            "area": area,
            "keypoints": keypoints,
            "num_keypoints": num_keypoints,
            "bbox": bbox,
            "iscrowd": iscrowd
        }
        self.now_annotation_id += 1
        self.annotations.append(annotation)

    def to_json(self, save_path):
        coco_data = {
            "info": self.info,
            "images": self.images,
            "categories": self.categories,
            "annotations": self.annotations
        }

        with open(save_path, 'w') as json_file:
            json.dump(coco_data, json_file)
