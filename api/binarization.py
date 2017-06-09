# -*- coding: utf-8 -*-
from django.conf import settings
import sys, os, os.path, subprocess, shutil

# Get the directory of ocropy script
ocropyDir = settings.BASE_DIR + "/ocropy"

# Get the directory which stores all input and output files
dataDir = settings.MEDIA_ROOT

# Execute ocr binarization script: binarize the original image
# Parameter: the original image name
# Return: a list conaining two files: {iamgename}.bin.png, {iamgename}.nrm.png
def binarization_exec(imagename):

    # Prepare path for OCR service
    inputPath = dataDir+"/"+imagename
    image_base = imagename.split(".")[0]
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


'''
# Get the directory which stores all input and output files
srcDir = settings.BASE_DIR + "/data/input/"
dstDir = settings.BASE_DIR + "/data/output/"

# Execute ocr binarization script: binarize the original image
# Parameter: the original image name
# Return: a related directory named according to the image name, containing two files: 0001.bin.png, 0001.nrm.png
def binarization_exec(imagename):

    # Prepare path for OCR service
    srcImagePath = srcDir + imagename
    image_name, image_extension = os.path.splitext(imagename)
    outputDir = dstDir + image_name
    
    # Call binarization script
    binarize_cmd = ocropyDir + "/ocropus-nlbin -n " + srcImagePath + " -o " + outputDir
    r_binarize = subprocess.call([binarize_cmd], shell=True)
    if r_binarize != 0:
        sys.exit("Error: Binarization process failed")

    return outputDir
'''

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

