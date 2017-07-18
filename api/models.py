# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from .validators import validate_image_extension


### The parameters that can be set by an service API call
class Parameters(models.Model):
	#image = models.ImageField(upload_to='', null=True, validators=[validate_image_extension])
	threshold = models.FloatField(default=0.5, help_text="threshold determines lightness")
	zoom = models.FloatField(default=0.5, help_text="zoom for page background estimation")
	escale = models.FloatField(default=1.0, help_text="scale for estimating a mask over the text region")
	bignore = models.FloatField(default=0.1, help_text="ignore this much of the border for threshold estimation")
	perc = models.FloatField(default=80.0, help_text="percentage for filters")
	range = models.IntegerField(default=20, help_text="range for filters")
	maxskew = models.FloatField(default=2.0, help_text="skew angle estimation parameters")
	lo = models.FloatField(default=5.0, help_text="percentile for black estimation")
	hi = models.FloatField(default=90.0, help_text="percentile for white estimation")
	skewsteps = models.IntegerField(default=8, help_text="steps for skew angle estimation (per degree)")

	parallel = models.IntegerField(default=0, help_text="number of parallel CPUs to use")
'''
class ParameterImage(models.Model):
	parameters = models.ForeignKey(Parameters, related_name='images')
	image = models.ImageField(upload_to='', validators=[validate_image_extension])
'''
