# -*- coding: utf-8 -*-
from django.conf import settings
from PIL import Image
from resizeimage import resizeimage # Used for image resize
import sys, os, os.path, subprocess, shutil

# Get the directory of ocropy script
ocropyDir = settings.BASE_DIR + "/ocropy"

# Get the directory which stores all input and output files
dataDir = settings.MEDIA_ROOT


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


# Execute ocr binarization script: binarize the original image
# Parameter: the original image name
# Return: a list conaining two files: {iamgename}.bin.png, {iamgename}.nrm.png
def binarization_exec(imagename):

    # Prepare path for OCR service
    inputPath = dataDir+"/"+imagename
    image_base, image_ext = os.path.splitext(imagename)
    outputfiles = []
    outputfiles.append(dataDir+"/"+image_base+".bin.png")
    outputfiles.append(dataDir+"/"+image_base+".nrm.png")
    
    # Call binarization script
    binarize_cmd = ocropyDir + "/ocropus-nlbin -n " + inputPath
    r_binarize = subprocess.call([binarize_cmd], shell=True)
    if r_binarize != 0:
        sys.exit("Error: Binarization process failed")

    if os.path.exists(outputfiles[0]) and os.path.exists(outputfiles[1]):
	return outputfiles
    else:
	sys.exit("Error: the output files do not exist.")


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

