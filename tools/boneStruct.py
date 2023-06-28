import numpy as np
import open3d as o3d

from tools.draw import draw_line_to_plane
from tools.other import cla_point, line_plane_intersection, find_largest_area, back_color


# 存单节骨头信息的结构
class BoneStruct:
    def __init__(self, category_id, markBox_3d, markPoint_3d, markPoint_Text, drawLine, cuboid_center, volume, spacing,
                 draw_box, draw_box_line, draw_point_line):
        # 参数
        self.category_id = category_id
        # 3d框中的两个角，分别为xyz最大最小的坐标，大坐标在前
        self.markBox_3d = markBox_3d
        # MIMICS [侧视图， 正视图， 俯视图]
        self.markPoint_3d = markPoint_3d
        # markPoint的注释
        self.markPoint_Text = markPoint_Text
        # 是否画线到平面
        self.drawLine = drawLine
        # lineBox是在3D上的框
        self.lineBox_3d = o3d.geometry.TriangleMesh.create_box(width=markBox_3d[0][0] - markBox_3d[1][0],
                                                               height=markBox_3d[0][1] - markBox_3d[1][1],
                                                               depth=markBox_3d[0][2] - markBox_3d[1][2])
        self.lineBox_3d.translate(cuboid_center)
        self.lineBox_3d.translate([markBox_3d[1][0], markBox_3d[1][1], volume[2] * spacing[2] - markBox_3d[0][2]])
        # 3D上的点
        self.pointlist_3d = []
        for point in markPoint_3d:
            cuboid_point = o3d.geometry.TriangleMesh.create_sphere(radius=3)
            cuboid_point.paint_uniform_color([1, 0, 0])
            cuboid_point.translate(cuboid_center)
            cuboid_point.translate([point[0], point[1], volume[2] * spacing[2] - point[2]])
            self.pointlist_3d.append(cuboid_point)

        # 环境变量
        self.cuboid_center = cuboid_center
        self.volume = volume
        self.spacing = spacing

        # 可视化
        self.draw_box_line = draw_box_line
        self.draw_point_line = draw_point_line
        self.draw_box = draw_box

        # 结果
        self.markPoint_2d = []
        self.markBox_2d = []

    # 解析出标志点在图像的位置
    def solve_2dPoint(self, sphere, plane, delx):
        for point in self.markPoint_3d:
            cuboid_point = o3d.geometry.TriangleMesh.create_sphere(radius=3)
            cuboid_point.translate(self.cuboid_center)
            cuboid_point.translate([point[0], point[1], self.volume[2] * self.spacing[2] - point[2]])
            plane_point = line_plane_intersection(sphere.get_center(), cuboid_point.get_center(), plane.vertices)
            x, y = cla_point(plane, plane_point, delx, True)
            self.markPoint_2d.append(
                [x, y]
            )

    # 解析出框在图像的位置
    def solve_2dBox(self, sphere, plane, delx):
        plane_point = plane.vertices
        points = []
        for i in range(0, 8):
            points.append(line_plane_intersection(
                sphere.get_center(), np.asarray(self.lineBox_3d.vertices)[i], plane_point))

        # 找到最大的图上面面积，即为框大小
        points = find_largest_area(points)

        points_2d = []

        for point in points:
            x, y = cla_point(plane, point, delx, False)
            points_2d.append([x, y])

        x_values = [item[0] for item in points_2d]
        y_values = [item[1] for item in points_2d]

        # 即不在目标框内或面积过小
        if (max(x_values) - min(x_values)) + (max(y_values) - min(y_values)) < 300 \
                or max(x_values) - min(x_values) < 200 \
                or max(y_values) - min(y_values) < 200:
            self.markBox_2d.append([-1, -1])
            self.markBox_2d.append([-1, -1])
        else:
            self.markBox_2d.append([min(x_values), min(y_values)])
            self.markBox_2d.append([max(x_values), max(y_values)])

    # 可视化：框到面的线
    def draw_line_markBox_3d_to_plane(self, sphere, plane, scene):
        if not self.draw_box_line:
            return scene
        plane_point = plane.vertices
        points = []
        for i in range(0, 8):
            points.append(line_plane_intersection(
                sphere.get_center(), np.asarray(self.lineBox_3d.vertices)[i], plane_point))

        # 找到最大的图上面面积，即为框大小
        points = find_largest_area(points)

        for i in points:
            line = o3d.geometry.LineSet()
            line.points = o3d.utility.Vector3dVector(
                [sphere.get_center(), i])
            line.lines = o3d.utility.Vector2iVector([[0, 1]])
            line.colors = o3d.utility.Vector3dVector([back_color()])
            scene.add_geometry(line)

        return scene

    # 可视化: 标志点在3d中显示
    def add_points_3d_to_scene(self, scene):
        for point in self.pointlist_3d:
            scene.add_geometry(point)

        return scene

    # 可视化：3d中显示框
    def add_mask_to_scene(self, scene):
        if not self.draw_box:
            return scene
        lines_mask = o3d.geometry.LineSet.create_from_triangle_mesh(self.lineBox_3d)
        scene.add_geometry(lines_mask)

        return scene

    # 可视化:3d中从相机到标志点到面的连线
    def draw_points_3d_to_plane_line(self, sphere, plane, scene):
        if not self.draw_point_line:
            return scene
        for point in self.pointlist_3d:
            draw_line_to_plane(plane, sphere, point.get_center(), scene)

        return scene


# 2d中框的信息
class MarkBox:
    def __init__(self, leftTop, leftDown, rightTop, rightDown):
        self.leftTop = leftTop
        self.leftDown = leftDown
        self.rightTop = rightTop
        self.rightDown = rightDown


# 2d中点的信息
class MarkPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
