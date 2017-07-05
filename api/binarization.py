#!/usr/bin/env python

from __future__ import print_function

from pylab import *
from numpy.ctypeslib import ndpointer
import os, os.path
from scipy.ndimage import filters, interpolation, morphology, measurements
from scipy import stats
import multiprocessing
import ocrolib


"""
Image binarization using non-linear processing.
This is a compute-intensive binarization method that works on degraded
and historical book pages.
"""

# The default parameters values
# Users can custom the first 10 parameters
args = {
### The following parameters can be overwritten by users
'threshold':0.5, # threshold, determines lightness
'zoom':0.5,      # zoom for page background estimation
'escale':1.0,    # scale for estimating a mask over the text region
'bignore':0.1,   # ignore this much of the border for threshold estimation
'perc':80.0,     # percentage for filters
'range':20,      # range for filters
'maxskew':2.0,   # skew angle estimation parameters
'lo':5.0,        # percentile for black estimation
'hi':90.0,       # percentile for white estimation
'skewsteps':8,   # steps for skew angle estimation (per degree)

### The following parameters needn't be overwritten by users
'nocheck':True,  # disable error checking on inputs
'parallel':0     # number of parallel processes to use
}

# The entry of binarization service
def binarization_exec(images, parameters):
    # Update parameters values customed by user
    args.update(parameters)
    print("==========")
    print(args)
    
    if len(images)<1:
        sys.exit(0)

    # Unicode to str
    for i, image in enumerate(images):
        images[i] = str(image)

    output_files = []

    if args['parallel']<2:
        for i,f in enumerate(images):
            output_list = process((f,i+1))
            output_files = output_files + output_list
    else:
        pool = multiprocessing.Pool(processes=args['parallel'])
        jobs = []
        for i,f in enumerate(images): jobs += [(f,i+1)]
        result = pool.map(process, jobs)
        for output_list in result:
            output_files = output_files + output_list
    return output_files
    

def print_info(*objs):
    print("INFO: ", *objs, file=sys.stdout)

def print_error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)

def check_page(image):
    if len(image.shape)==3: return "input image is color image %s"%(image.shape,)
    if mean(image)<median(image): return "image may be inverted"
    h,w = image.shape
    if h<600: return "image not tall enough for a page image %s"%(image.shape,)
    if h>10000: return "image too tall for a page image %s"%(image.shape,)
    if w<600: return "image too narrow for a page image %s"%(image.shape,)
    if w>10000: return "line too wide for a page image %s"%(image.shape,)
    return None

def estimate_skew_angle(image,angles):
    estimates = []
    for a in angles:
        v = mean(interpolation.rotate(image,a,order=0,mode='constant'),axis=1)
        v = var(v)
        estimates.append((v,a))
    _,a = max(estimates)
    return a

def H(s): return s[0].stop-s[0].start
def W(s): return s[1].stop-s[1].start
def A(s): return W(s)*H(s)



def process(job):
    fname,i = job
    print_info("# %s" % (fname))
    if args['parallel']<2: print_info("=== %s %-3d" % (fname, i))
    raw = ocrolib.read_image_gray(fname)

    # perform image normalization
    image = raw-amin(raw)
    if amax(image)==amin(image):
        print_info("# image is empty: %s" % (fname))
        return
    image /= amax(image)

    if not args['nocheck']:
        check = check_page(amax(image)-image)
        if check is not None:
            print_error(fname+"SKIPPED"+check+"(use -n to disable this check)")
            return

    # flatten the image by estimating the local whitelevel
    comment = ""
    # if not, we need to flatten it by estimating the local whitelevel
    if args['parallel']<2: print_info("flattening")
    m = interpolation.zoom(image,args['zoom'])
    m = filters.percentile_filter(m,args['perc'],size=(args['range'],2))
    m = filters.percentile_filter(m,args['perc'],size=(2,args['range']))
    m = interpolation.zoom(m,1.0/args['zoom'])
    w,h = minimum(array(image.shape),array(m.shape))
    flat = clip(image[:w,:h]-m[:w,:h]+1,0,1)

    # estimate skew angle and rotate
    if args['maxskew']>0:
        if args['parallel']<2: print_info("estimating skew angle")
        d0,d1 = flat.shape
        o0,o1 = int(args['bignore']*d0),int(args['bignore']*d1)
        flat = amax(flat)-flat
        flat -= amin(flat)
        est = flat[o0:d0-o0,o1:d1-o1]
        ma = args['maxskew']
        ms = int(2*args['maxskew']*args['skewsteps'])
        angle = estimate_skew_angle(est,linspace(-ma,ma,ms+1))
        flat = interpolation.rotate(flat,angle,mode='constant',reshape=0)
        flat = amax(flat)-flat
    else:
        angle = 0

    # estimate low and high thresholds
    if args['parallel']<2: print_info("estimating thresholds")
    d0,d1 = flat.shape
    o0,o1 = int(args['bignore']*d0),int(args['bignore']*d1)
    est = flat[o0:d0-o0,o1:d1-o1]
    if args['escale']>0:
        # by default, we use only regions that contain
        # significant variance; this makes the percentile
        # based low and high estimates more reliable
        e = args['escale']
        v = est-filters.gaussian_filter(est,e*20.0)
        v = filters.gaussian_filter(v**2,e*20.0)**0.5
        v = (v>0.3*amax(v))
        v = morphology.binary_dilation(v,structure=ones((int(e*50),1)))
        v = morphology.binary_dilation(v,structure=ones((1,int(e*50))))
        est = est[v]
    lo = stats.scoreatpercentile(est.ravel(),args['lo'])
    hi = stats.scoreatpercentile(est.ravel(),args['hi'])
    # rescale the image to get the gray scale image
    if args['parallel']<2: print_info("rescaling")
    flat -= lo
    flat /= (hi-lo)
    flat = clip(flat,0,1)
    bin = 1*(flat>args['threshold'])

    # output the normalized grayscale and the thresholded images
    print_info("%s lo-hi (%.2f %.2f) angle %4.1f %s" % (fname, lo, hi, angle, comment))
    if args['parallel']<2: print_info("writing")
    base,_ = ocrolib.allsplitext(fname)
    outputfile_bin = base+".bin.png"
    outputfile_nrm = base+".nrm.png"
    output_files = [outputfile_bin, outputfile_nrm]
    ocrolib.write_image_binary(outputfile_bin, bin)
    ocrolib.write_image_gray(outputfile_nrm, flat)
    return output_files