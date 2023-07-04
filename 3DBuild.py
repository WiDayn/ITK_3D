import json

import open3d as o3d
import nibabel as nib

from tools.boneStruct import BoneStruct
from tools.drawMark import drawMark
from tools.genDRR import genDRR


# 这个是用来生成单张的图像和展示3D效果的
def main():
    with open('data/data.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    id = 1

    categoryMap = {}

    for categoryNumsText in json_data['category']['categoryNumsText']:
        categoryMap[categoryNumsText] = id
        id += 1

    for CTJSON in json_data['CTList']:
        if CTJSON["name"] != "wxt":
            continue

        sdr = CTJSON["sdr"]
        height = CTJSON["height"]
        delx = CTJSON["delx"]

        ctDir = CTJSON["DCMFilePath"]

        ct_image = nib.load(ctDir)
        header = ct_image.header
        volume = ct_image.shape
        spacing = header['pixdim'][1:4]
        cuboid_center = [0, 0, CTJSON["sdr"]]

        # 加载3D模型，并且移动到方框内
        mesh = o3d.io.read_triangle_mesh(CTJSON["3DPlyPath"])

        rotations = [90, 90, 0]
        translations = [0, -0, -0]

        saveIMG = "image.png"

        boneList = []

        for BoneJson in CTJSON['boneList']:
            boneList.append(
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

        genDRR(sdr, height, delx, rotations, translations, ctDir, saveIMG)

        drawMark(volume, spacing, sdr, height, delx, rotations, translations, saveIMG, 1, mesh, False, False, None,
                 boneList)


if __name__ == "__main__":
    main()
