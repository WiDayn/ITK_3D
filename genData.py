import csv
import json

import numpy as np
import nibabel as nib

from tools.COCOData import COCOData
from tools.boneStruct import CTStruct, BoneStruct
from tools.drawMark import drawMark
from tools.genDRR import genDRR


# 随机生成参数
def sample_dataset(rot_range, trans_range, num_samples):
    rotations = []
    translations = []
    for _ in range(num_samples):
        rotation = np.random.uniform(*rot_range, size=3)
        rotations.append(rotation)

        translation = np.random.uniform(*trans_range, size=3)
        translations.append(translation)

    return rotations, translations


dataSet = COCOData()
categoryMap = {}

with open('data/data.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

id = 1

for categoryNumsText in json_data['category']['categoryNumsText']:
    categoryMap[categoryNumsText] = id
    dataSet.add_category(id, categoryNumsText, "object",
                         keypoints=['left_pedicle', 'right_pedicle', 'centrum_top', 'centrum_down'],
                         skeleton=[])
    id += 1

# 依次处理每一个CT
i = 1

for CTJSON in json_data['CTList']:
    # 参数范围
    rot_range = (-180, 180)
    trans_range = (-75, 75)
    num_samples = 1
    rotations, translations = sample_dataset(rot_range, trans_range, num_samples)


    ct = CTStruct(CTJSON["DCMFilePath"])
    cuboid_center = [0, 0, CTJSON["sdr"]]

    sdr = CTJSON["sdr"]
    height = CTJSON["height"]
    delx = CTJSON["delx"]

    ctDir = CTJSON["DCMFilePath"]
    ct_image = nib.load(ctDir)
    header = ct_image.header
    volume = ct_image.shape
    spacing = header['pixdim'][1:4]

    for BoneJson in CTJSON['boneList']:
        ct.boneStruct.append(
            BoneStruct(
                category_id=categoryMap[BoneJson["category_name"]],
                markBox_3d=BoneJson['markBox_3d'],
                markPoint_3d=BoneJson['markPoint_3d'],
                drawLine=True,
                cuboid_center=cuboid_center,
                volume=volume,
                spacing=spacing,
                draw_box=False,
                draw_box_line=False,
                draw_point_line=False,
            )
        )

    for rotation, translation in zip(rotations, translations):
        saveDir = './dataset'
        saveIMG = f"{i:09d}" + '.png'

        ct_image = nib.load(ctDir)
        header = ct_image.header
        volume = ct_image.shape
        spacing = header['pixdim'][1:4]

        genDRR(sdr, height, delx, rotation, translation, ctDir, saveDir + '/' + saveIMG)

        dataSet.add_image(i, height, height, saveIMG)

        drawMark(volume, spacing, sdr, height, delx, rotation, translation, saveDir + '/' + saveIMG, i, None, True,
                 False, dataSet, ct.boneStruct)

        i += 1
        print("Now ID: ", i)
        print("Rotation angles:", rotation)
        print("Translations:", translation)

dataSet.to_json("coco_data.json")
print("Done!")
