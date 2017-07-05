# -*- coding: utf-8 -*-
from PIL import Image
from resizeimage import resizeimage # Used for image resize
import sys, os, os.path, shutil

'''
This module rpovides extra functions: resize image
and delete all of the data generated during process.
'''

# Resize the image size to meet the smallest size requirment of binarization: 600*600 pixels
# Resize by adding a white backgroud border, but not to strech the original image
def resize_image(imagepath):
    fd_img = open(imagepath, 'r')
    img = Image.open(fd_img)
    w, h = img.size
    if w<600 or h<600:
        if w<600: w = 600
        if h<600: h = 600
        new_size = [w, h]
        new_image = resizeimage.resize_contain(img, new_size)
        new_image.save(imagepath, new_image.format) # override the original image
        fd_img.close()
    else:
        pass


# Delete all files related to this service time, including inputs and outputs
def del_service_files(dataDir):
    for the_file in os.listdir(dataDir):
        file_path = os.path.join(dataDir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)