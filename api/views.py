# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from wsgiref.util import FileWrapper
from .binarization import resize_image, binarization_exec, del_service_files
import sys, os, os.path, zipfile, StringIO

# Set encoding
reload(sys)
sys.setdefaultencoding('utf8')

# Get the directory which stores all input and output files
dataDir = settings.MEDIA_ROOT

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def binarizationView(request, format=None):

    # Receive uploaded image(s)
    keys = request.data.keys()
    if len(keys)<1:
	return HttpResponse("Please selecting at least one image.")
    imagenames = []
    '''
    # Only one file/value in each field
    for key in keys:
	uploadedimage = request.data.get(key)
	image_str = str(uploadedimage)
	imagenames.append(image_str)
    	default_storage.save(dataDir+"/"+image_str, uploadedimage)

    '''
    # One or multiple files/values in one field
    for key in keys:
	uploadedimages = request.data.getlist(key)
	print("######## %d" % len(uploadedimages))
	if len(uploadedimages) == 1:
	    image_str = str(uploadedimages[0])
	    imagenames.append(image_str)
    	    default_storage.save(dataDir+"/"+image_str, uploadedimages[0])
	elif len(uploadedimages) > 1:
	    for image in uploadedimages:
		image_str = str(image)
		imagenames.append(image_str)
		default_storage.save(dataDir+"/"+image_str, image)
    	
    # Resize the image if its size smaller than 600*600
    for imagename in imagenames:
	imagepath = dataDir+"/"+imagename
	resize_image(imagepath)

    # Call OCR binarization function
    output_files = []
    for imagename in imagenames:
	output_list = binarization_exec(imagename)
	output_files.extend(output_list)

    # return multiple files in zip type
    # Folder name in ZIP archive which contains the above files
    zip_subdir = "output_of_binarization"
    zip_filename = "%s.zip" % zip_subdir
    # Open StringIO to grab in-memory ZIP contents
    strio = StringIO.StringIO()
    # The zip compressor
    zf = zipfile.ZipFile(strio, "w")

    for fpath in output_files:
        # Caculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        # Add file, at correct path
        zf.write(fpath, zip_path)

    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(strio.getvalue(), content_type="application/x-zip-compressed")
    # And correct content-disposition
    response["Content-Disposition"] = 'attachment; filename=%s' % zip_filename
    
    # Delete all files related to this service time
    del_service_files(dataDir)

    return response

'''
## binarization specify and return output directory, but the output file name is fixed to 0001.bin.png and 0001.nrm.png 
@csrf_exempt
@api_view(['GET', 'POST'])
def binarizationView(request, format=None):

    # Receive uploaded image(s)
    keys = request.data.keys()
    if len(keys)<1:
	return HttpResponse("Please selecting at least one image.")
    imagenames = []
    for index, key in enumerate(keys):
	uploadedimage = request.data.get(key)
	imagenames.append(str(uploadedimage))
    	default_storage.save(srcImageDir + imagenames[index], uploadedimage)
	
    # Call OCR function
    output_dirs = []
    for index, imagename in enumerate(imagenames):
	output_dir = binarization_exec(imagename)
	output_dirs.append(output_dir)

    # Put all output files path in a list
    outputfiles_path = []
    for output_dir in output_dirs:
	for output_file  in os.listdir(output_dir):
	    file_path = os.path.join(output_dir, output_file)
	    outputfiles_path.append(file_path)

    # return the multiple files in zip type
    # Folder name in ZIP archive which contains the above files
    zip_dir = "output_of_bin"
    zip_filename = "%s.zip" % zip_dir
    # Open StringIO to grab in-memory ZIP contents
    strio = StringIO.StringIO()
    # The zip compressor
    zf = zipfile.ZipFile(strio, "w")

    for fpath in outputfiles_path:
        # Caculate path for file in zip
        fdir, fname = os.path.split(fpath)
	subdir = os.path.basename(os.path.normpath(fdir))
        zip_path = os.path.join(zip_dir+"/"+subdir, fname)
        # Add file, at correct path
        zf.write(fpath, zip_path)

    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(strio.getvalue(), content_type="application/x-zip-compressed")
    # And correct content-disposition
    response["Content-Disposition"] = 'attachment; filename=%s' % zip_filename
    
    # Delete all files related to this service time
    #del_service_files()

    return response
'''
