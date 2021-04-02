from django.db import models
# import glob, re
import numpy as np
import pandas as pd
from core.models import NirProfile
from django.core.exceptions import ValidationError
# from matplotlib import pyplot as plt
# from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA
# from sklearn.decomposition import PCA
from scipy.signal import savgol_filter

# def moving_average(x, w):
#     return np.convolve(x, np.ones(w), 'valid') / w

# def savgol_average(x, w, p):
#     return savgol_filter(x, w, p, deriv=2,mode='mirror')
def validate_window(value):
    if not value%2:
        raise ValidationError('please select an odd number.')

class SgFilter(models.Model): # for SavitzkyGolay filter
    MODEL_CHOICES = [
        ('M', 'Mirror'),
        ('C', 'Constant'),
        ('N', 'Nearest'),
        ('W', 'wrap'),
        ('I', 'Interp'),
    ]
    
    # title = models.TextField(blank=True, null=True, max_length=100)
    window_length = models.IntegerField(default= 13, validators=[validate_window])
    polyorder = models.IntegerField(default = 2)
    deriv = models.IntegerField(default = 2)
    mode = models.CharField(max_length=1, choices=MODEL_CHOICES, default='M')
    y_axis = models.TextField(blank=True, null=True)
    
    nirprofile = models.ManyToManyField(NirProfile) #on_delete=DO_NOTHING

    def __str__(self):
        return self.nirprofile.first().title + ', window: '+ str(self.window_length)

    def y(self):
        return np.array(eval(self.y_axis))

    def obtain(self, **kwargs):  #ips,window_length,polyorder,deriv,mode
        ids=kwargs['ids']
        _=kwargs.pop('ids')
        for i in kwargs:
            exec('self.'+i+'= kwargs["'+i+'"]')
        # self.save()
        spectra=[]
        for i in ids:
            spectra.extend([j.y().tolist() for j in NirProfile.objects.get(id=i).spectrum_set.all()])
        spectra=np.array(spectra)
        # self.save()
        self.y_axis=str(self.savgol(spectra).tolist())
        # self.nirprofile.set(ids)
        # self.save()

    def savgol(self,x):
        mode=dict(self.MODEL_CHOICES)[self.mode].lower()
        return savgol_filter(x, self.window_length, self.polyorder, deriv=self.deriv,mode=mode )

    def get_absolute_url(self):
        return '/sgfilter/'+self.id+'/'


#     Apply savgol_average:
# np.array2string(x)
# # s1=np.array([savgol_average(i,13,2) for i in os1.tolist()])

