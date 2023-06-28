import open3d as o3d
import nibabel as nib

from tools.drawMark import drawMark
from tools.genDRR import genDRR


# 这个是用来生成单张的图像和展示3D效果的
def main():
    sdr = 500.0
    height = 1000
    delx = 0.25
    ctDir = "./504 1.0 x 0.5_bone.nii.gz"
    saveIMG = './image.png'

    ct_image = nib.load(ctDir)
    header = ct_image.header
    volume = ct_image.shape
    spacing = header['pixdim'][1:4]

    # 加载3D模型，并且移动到方框内
    mesh = o3d.io.read_triangle_mesh("./3d_full.ply")

    rotations = [90, 90, 90]
    translations = [-0, -0, -0]
    # translations = [-volume[0] * spacing[0] / 2, -volume[1] * spacing[1] / 2, 0]

    genDRR(sdr, height, delx, rotations, translations, ctDir, saveIMG)

    drawMark(volume, spacing, sdr, height, delx, rotations, translations, saveIMG, 1, mesh, False, False, dataSet=None)


if __name__ == "__main__":
    main()
