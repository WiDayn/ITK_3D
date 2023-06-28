import matplotlib.pyplot as plt
from PIL import Image


def mark_points_on_image(image_path, boneList):
    # 打开PNG图像
    image = Image.open(image_path)

    # 显示图像
    plt.imshow(image)

    # 标出给定的点
    for bone in boneList:
        if bone.markBox_2d[0][0] == -1 or bone.markBox_2d[0][1] == -1:
            continue

        for point in bone.markPoint_2d:
            x, y = point[0], point[1]
            if x == -1 or y == -1:
                continue
            plt.scatter(x, y, s=50, c='red', edgecolor='red')

        x = [bone.markBox_2d[0][0], bone.markBox_2d[1][0], bone.markBox_2d[1][0], bone.markBox_2d[0][0]]
        y = [bone.markBox_2d[0][1], bone.markBox_2d[0][1], bone.markBox_2d[1][1], bone.markBox_2d[1][1]]
        # 添加第一个点到最后，以闭合矩形
        x.append(x[0])
        y.append(y[0])
        # 画出矩形
        plt.plot(x, y, '-')


    # 显示标记后的图像
    plt.show()
