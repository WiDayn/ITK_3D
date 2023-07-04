import json
import math

import numpy as np
import open3d as o3d
import open3d.visualization as vis
import torch

from tools.boneStruct import BoneStruct
from tools.other import line_plane_intersection, back_color
from tools.vis_png import mark_points_on_image

# is_gen 生成数据集模式 show3d 显示3d窗口
def drawMark(volume, spacing, sdr, height, delx, rotations, translations, saveIMG, imgID, mesh, is_gen, show3d,
             dataSet, boneList):
    scene = o3d.visualization.Visualizer()

    if not is_gen:
        scene.create_window()

    plane_size = height * delx
    sphere_center = [0, 0, sdr]
    plane_center = [0, 0, -sdr]
    cuboid_center = [0, 0, sdr]

    # 相机
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1)
    sphere.paint_uniform_color([1, 0, 0])

    # 零点
    cuboid_zero = o3d.geometry.TriangleMesh.create_sphere(radius=3)
    cuboid_zero.paint_uniform_color([1, 0, 0])
    cuboid_zero.translate(cuboid_center)

    # 物体边框
    cuboid = o3d.geometry.TriangleMesh.create_box(width=volume[0] * spacing[0],
                                                  height=volume[1] * spacing[1],
                                                  depth=volume[2] * spacing[2])

    # 平面的三角网格，并加载一张图片作为纹理
    plane = o3d.geometry.TriangleMesh()
    half_plane_size = plane_size / 2.0

    plane.vertices = o3d.utility.Vector3dVector(
        [[half_plane_size, half_plane_size, 0], [-half_plane_size, half_plane_size, 0],
         [-half_plane_size, -half_plane_size, 0], [half_plane_size, -half_plane_size, 0]]
    )
    plane.triangles = o3d.utility.Vector3iVector([[0, 1, 2], [0, 2, 3]])

    texture_image = o3d.io.read_image(saveIMG)
    texture = o3d.geometry.Image(texture_image)
    plane.triangle_uvs = o3d.utility.Vector2dVector(
        np.array([[1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    )
    faces = np.array(plane.triangles)
    plane.triangle_material_ids = o3d.utility.IntVector([0] * len(faces))
    plane.textures = [texture]

    # 将其移动到两侧，便于后续的旋转操作
    sphere.translate(sphere_center)
    plane.translate(plane_center)

    # 创建旋转矩阵，应用rotations，注意pitch角取反
    rotation_matrix = np.eye(4)
    rot = [math.radians(rotations[0]), 0, 0]
    rotation_matrix[:3, :3] = o3d.geometry.get_rotation_matrix_from_xyz(rot)
    sphere.transform(rotation_matrix)
    plane.transform(rotation_matrix)

    rot = [0, math.radians(-rotations[1]), 0]
    rotation_matrix[:3, :3] = o3d.geometry.get_rotation_matrix_from_xyz(rot)
    sphere.transform(rotation_matrix)
    plane.transform(rotation_matrix)

    rot = [0, 0, math.radians(-rotations[2])]
    rotation_matrix[:3, :3] = o3d.geometry.get_rotation_matrix_from_xyz(rot)
    sphere.transform(rotation_matrix)
    plane.transform(rotation_matrix)

    # 移动到sdr,整个模型以sdr为中心
    cuboid.translate(cuboid_center)
    # 先移动到原点，让其绕自己旋转
    # print(-mesh.get_center())
    # print([-volume[0] * spacing[0] / 2.0, -volume[1] * spacing[1] / 2.0, -volume[2] * spacing[2] / 2.0])
    # mesh.translate([-volume[0] * spacing[0] / 2.0, -volume[1] * spacing[1] / 2.0, -volume[2] * spacing[2] / 2.0])
    if not is_gen:
        mesh.translate(-mesh.get_center())
        rotation_matrix = np.eye(4)
        rotation_matrix[:3, :3] = o3d.geometry.get_rotation_matrix_from_xyz([0, torch.pi, -torch.pi])
        mesh.transform(rotation_matrix)
        # # 移动到sdr
        mesh.translate([volume[0] * spacing[0] / 2, volume[1] * spacing[1] / 2, sdr + volume[2] * spacing[2] / 2.0])

    # 创建平移变换
    translation = [volume[0] * spacing[0] / 2, volume[1] * spacing[1] / 2, sdr + volume[2] * spacing[2] / 2.0]
    T = np.eye(4)
    T[:3, 3] = translation
    sphere.transform(T)
    plane.transform(T)

    # 应用transform
    translation = [translations[0], -translations[1], -translations[2]]
    T = np.eye(4)
    T[:3, 3] = translation
    sphere.transform(T)
    plane.transform(T)

    for bone in boneList:
        bone.solve_2dPoint(sphere, plane, delx)
        bone.solve_2dBox(sphere, plane, delx)

    if is_gen:
        for bone in boneList:
            if bone.markBox_2d[0][0] != -1 and bone.markBox_2d[0][1] != -1:
                points = []
                validPointCount = 0
                for point in bone.markPoint_2d:
                    if point[0] != -1 and point[1] != -1:
                        points.append(point[0])
                        points.append(point[1])
                        points.append(2)
                        validPointCount += 1
                    else:
                        points.append(0)
                        points.append(0)
                        points.append(0)

                dataSet.add_annotation_object(imgID, bone.category_id, [],
                                              (bone.markBox_2d[1][0] - bone.markBox_2d[0][0]) * (
                                                      bone.markBox_2d[1][1] - bone.markBox_2d[0][1]),
                                              validPointCount,
                                              points,
                                              [bone.markBox_2d[0][0], bone.markBox_2d[0][1],
                                               bone.markBox_2d[1][0] - bone.markBox_2d[0][0],
                                               bone.markBox_2d[1][1] - bone.markBox_2d[0][1]
                                               ])
        return
    else:
        # 渲染场景
        # 用于显示3D模型边框线条
        lines = o3d.geometry.LineSet.create_from_triangle_mesh(cuboid)

        for bone in boneList:
            scene = bone.add_points_3d_to_scene(scene)
            scene = bone.add_mask_to_scene(scene)
            scene = bone.draw_line_markBox_3d_to_plane(sphere, plane, scene)
            scene = bone.draw_points_3d_to_plane_line(sphere, plane, scene)

        # 相机方向指示线
        # draw_camera_line(sphere, plane, scene)

        # 这四条是指示图像边界的
        # draw_boarder(plane, sphere, cuboid, scene)

        # 指示mask边界

        # 到平面中心的线
        # draw_center_line(sphere, plane, scene)

        # testp = o3d.geometry.TriangleMesh.create_sphere(radius=5)
        # testp.paint_uniform_color([1, 0, 0])
        # testp.translate([-50, -50, 68])
        # scene.add_geometry(testp)

        scene.add_geometry(mesh)
        scene.add_geometry(sphere)
        scene.add_geometry(plane)
        scene.add_geometry(lines)
        scene.add_geometry(cuboid_zero)

        opt = scene.get_render_option()
        opt.background_color = np.asarray([0.7, 0.85, 1.0])  # 设置为灰色背景
        opt.line_width = 30

        mark_points_on_image(saveIMG, boneList)
        if show3d:
            scene.run()
            scene.destroy_window()


def draw_camera_line(sphere, plane, scene):
    for i in range(0, 2):
        line = o3d.geometry.LineSet()
        line.points = o3d.utility.Vector3dVector(
            [sphere.get_center(), np.asarray(plane.vertices)[i]])
        line.lines = o3d.utility.Vector2iVector([[0, 1]])
        line.colors = o3d.utility.Vector3dVector([[1, 0, 0]])
        scene.add_geometry(line)


def draw_center_line(sphere, plane, scene):
    line_center = o3d.geometry.LineSet()
    line_center.points = o3d.utility.Vector3dVector([sphere.get_center(), plane.get_center()])
    line_center.lines = o3d.utility.Vector2iVector([[0, 1]])
    line_center.colors = o3d.utility.Vector3dVector([[1, 0, 1]])
    scene.add_geometry(line_center)


def draw_boarder(plane, sphere, cuboid, scene):
    plane_point = plane.vertices
    for i in range(2, 4):
        line = o3d.geometry.LineSet()
        line.points = o3d.utility.Vector3dVector(
            [sphere.get_center(), line_plane_intersection(
                sphere.get_center(), np.asarray(cuboid.vertices)[i], plane_point)])
        line.lines = o3d.utility.Vector2iVector([[0, 1]])
        line.colors = o3d.utility.Vector3dVector([back_color()])
        scene.add_geometry(line)

    for i in range(6, 8):
        line = o3d.geometry.LineSet()
        line.points = o3d.utility.Vector3dVector(
            [sphere.get_center(), line_plane_intersection(
                sphere.get_center(), np.asarray(cuboid.vertices)[i], plane_point)])
        line.lines = o3d.utility.Vector2iVector([[0, 1]])
        line.colors = o3d.utility.Vector3dVector([back_color()])
        scene.add_geometry(line)
