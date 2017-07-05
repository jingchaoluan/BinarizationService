# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.decorators import api_view, parser_classes
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from wsgiref.util import FileWrapper
from .models import Parameters
from .binarization import binarization_exec
from .extrafunc import resize_image, del_service_files
from .serializers import ParameterSerializer
import sys, os, os.path, zipfile, StringIO
import json

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
    if request.data.get('image') is None:
        return HttpResponse("Please upload at least one image.")
    
    # Receive parameters with model and serializer
    data_dict = request.data.dict()
    del data_dict['image']   # Image will be processed seperately for receiving multiple images
    # Serialize the specified parameters, only containing the specified parameters
    # If we want to generate the parameters object with all of the default paremeters, call parameters.save()
    paras_serializer = ParameterSerializer(data=data_dict)
    if paras_serializer.is_valid():
        pass # needn't parameters.save(), since we needn't to store these parameters in DB
    
    # Another to receive specified parameters values without model and serializer
    # But complex to process the format of different parameters type
    '''
    parameters = {}
    keys = request.data.keys()
    keys.remove('image')
    for key in keys:
        # Store unicode data in utf-8 format, convert value format from string to float
        parameters[key.encode('utf-8')] = float(request.data.get(key).encode('utf-8'))
    '''

    # Receive and store uploaded image(s)
    # One or multiple images/values in one field
    imagenames = []
    images = request.data.getlist('image')
    for image in images:
        image_str = str(image)
        imagenames.append(image_str)
        default_storage.save(dataDir+"/"+image_str, image)

    # Resize the image if its size smaller than 600*600
    imagepaths = []
    for imagename in imagenames:
        imagepath = dataDir+"/"+imagename
        imagepaths.append(imagepath)
        resize_image(imagepath)

    # Call OCR binarization function
    output_files = []
    output_files = binarization_exec(imagepaths, paras_serializer.data)
    
    ### Generate return file ###
    # Return multiple files in zip type.
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