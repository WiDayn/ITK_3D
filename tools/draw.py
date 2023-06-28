import open3d as o3d

from tools.other import line_plane_intersection, back_color


def draw_line_to_plane(plane, sphere, point, scene):
    plane_point = plane.vertices
    line = o3d.geometry.LineSet()
    line.points = o3d.utility.Vector3dVector(
        [sphere.get_center(), line_plane_intersection(
            sphere.get_center(), point, plane_point)])
    line.lines = o3d.utility.Vector2iVector([[0, 1]])
    line.colors = o3d.utility.Vector3dVector([back_color()])
    scene.add_geometry(line)
    return line_plane_intersection(sphere.get_center(), point, plane_point)