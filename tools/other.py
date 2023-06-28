import itertools
import random

import numpy as np


def back_color():
    ran = random.randint(0, 3)
    if ran == 0:
        return [1, 1, 0]
    if ran == 1:
        return [0, 1, 0]
    if ran == 2:
        return [0, 0, 1]
    if ran == 3:
        return [1, 0, 1]


# 如果是标志点，则超出需要返回不存在（-1），如果是框，则改到边界处
def cla_point(plane, point, delx, is_mark_point):
    A = np.array(plane.vertices[1])
    B = np.array(plane.vertices[0])
    D = np.array(plane.vertices[2])

    P = np.array(point)

    # 计算法向量
    AB = B - A
    AD = D - A

    # 计算向量 AP 在 AB 和 AD 方向上的投影长度
    AP = P - A
    t1 = np.dot(AP, AB) / np.dot(AB, AB)
    t2 = np.dot(AP, AD) / np.dot(AD, AD)

    if t1 < 0 or t1 > 1 or t2 < 0 or t2 > 1:
        if is_mark_point:
            return -1, -1
        else:
            t1 = min(max(0.0, t1), 0.999)
            t2 = min(max(0.0, t2), 0.999)

    return t1 * np.linalg.norm(AB) / delx, t2 * np.linalg.norm(AD) / delx


def calculate_area(points):
    A = np.array(points[0])
    B = np.array(points[1])
    C = np.array(points[2])
    D = np.array(points[3])

    # 计算三角形ABC的面积
    area_ABC = 0.5 * np.linalg.norm(np.cross(B - A, C - A))

    # 计算三角形BCD的面积
    area_BCD = 0.5 * np.linalg.norm(np.cross(C - B, C - D))

    # 计算四边形ABCD的面积
    area = area_ABC + area_BCD

    return area


def find_largest_area(points):
    max_area = 0.0
    max_points = []

    # 使用itertools的组合函数找出所有可能的四个点的组合
    combinations = itertools.combinations(points, 4)
    for combination in combinations:
        area = calculate_area(combination)
        if area > max_area:
            max_area = area
            max_points = combination

    return max_points


# 计算点面交点
def line_plane_intersection(line_point, line_point_2, plane_points):
    # 将点和向量转换为NumPy数组
    line_point = np.array(line_point)
    line_direction = np.array(line_point) - np.array(line_point_2)
    plane_points = np.array(plane_points)

    # 计算平面的法向量
    plane_normal = np.cross(plane_points[1] - plane_points[0], plane_points[2] - plane_points[0])

    # 计算线与平面的交点
    t = np.dot(plane_normal, (plane_points[0] - line_point)) / np.dot(plane_normal, line_direction)
    intersection_point = line_point + t * line_direction

    return intersection_point
