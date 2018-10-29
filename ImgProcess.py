import os
import sys
import pytesseract
from PIL import Image

# 将黑白图片转化为0-1矩阵
def img2txt(img):
    width, height = img.size
    pixStr = ""
    for j in range(1, height):
        for i in range(1, width):
            p = img.getpixel((i, j))
            if p == 255:
                pixStr += "0"
            else:
                pixStr += "1"
        pixStr += "\n"
    return pixStr

# 将图片黑白化，易于处理
def imgProcess(img, path):
    img = img.convert('L')  # 转为灰度图像
    table = []
    threshold = 120
    for i in range(256):
        if i > threshold:
            table.append(255)
        else:
            table.append(0)
    img = img.point(table, "1")
    return img

# 将验证码图片分割成4部分
def imgCrop(img, path):
    for i in range(4):
        img_crop = img.crop((4 + i * 12, 5, 16 + i * 12, 17))
        img_crop = imgProcess(img_crop, path)
        img_crop_txt = img2txt(img_crop)
        with open(path + str(i + 1) + ".txt", "wb") as fh:
            fh.write(img_crop_txt.encode("utf-8"))
        img_crop.save(path + str(i + 1) + ".jpg")

        

