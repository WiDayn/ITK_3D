import csv

import numpy as np
import nibabel as nib

from tools.COCOData import COCOData
from tools.drawMark import drawMark
from tools.genDRR import genDRR

dataSet = COCOData()
dataSet.add_category(1, "L1", "object",
                     keypoints=['Left pedicle', 'Right pedicle', 'Centrum top', 'Centrum down'],
                     skeleton=[])
dataSet.add_category(2, "L2", "object",
                     keypoints=['Left pedicle', 'Right pedicle', 'Centrum top', 'Centrum down'],
                     skeleton=[])
dataSet.add_category(3, "T12", "object",
                     keypoints=['Left pedicle', 'Right pedicle', 'Centrum top', 'Centrum down'],
                     skeleton=[])
dataSet.add_category(4, "T11", "object",
                     keypoints=['Left pedicle', 'Right pedicle', 'Centrum top', 'Centrum down'],
                     skeleton=[])

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


# 参数范围
rot_range = (-180, 180)
trans_range = (-75, 75)
num_samples = 100000

rotations, translations = sample_dataset(rot_range, trans_range, num_samples)

i = 1

for rotation, translation in zip(rotations, translations):
    sdr = 500.0
    height = 1000
    delx = 0.25
    ctDir = "./504 1.0 x 0.5_bone.nii.gz"
    saveDir = './dataset'
    saveIMG = f"{i:09d}" + '.png'

    ct_image = nib.load(ctDir)
    header = ct_image.header
    volume = ct_image.shape
    spacing = header['pixdim'][1:4]

    genDRR(sdr, height, delx, rotation, translation, ctDir, saveDir + '/' + saveIMG)

    dataSet.add_image(i, height, height, saveIMG)

    drawMark(volume, spacing, sdr, height, delx, rotation, translation, saveDir + '/' + saveIMG, i, None, True, dataSet)

    i += 1
    print("Now ID: ", i)
    print("Rotation angles:", rotation)
    print("Translations:", translation)

dataSet.to_json("coco_data.json")
print("Done!")
