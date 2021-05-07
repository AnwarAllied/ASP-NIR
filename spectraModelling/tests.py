from django.test import TestCase
from masterModelling.models import StaticModel
from spectraModelling.models import Match
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scal

from core.models import NirProfile, Spectrum
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
# from sklearn.linear_model import LinearRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA
from sklearn.cluster import KMeans
from chartjs.colors import next_color

# exec(open('spectraModelling/tests.py','r').read())

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def savgol(x, w, p):
    return savgol_filter(x, w, p, deriv=2,mode='mirror')

def min_max_scal(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)

def plot(x,*arg):
    arg=[''] if not arg else arg
    if len(arg[0])<2:
        if type(x) is tuple:
            x1,x2=x
            plt.plot(x1,x2,arg[0]);plt.show()
        else:
            plt.plot(x,arg[0]);plt.show()
    else:
        if type(x) is tuple:
            x1,x2=x
            _=plt.plot(x1,x2.T);plt.title(arg[0]);plt.ylabel(arg[1]);plt.xlabel(arg[2]);plt.show()
        else:
            _=plt.plot(x);plt.title(arg[0]);plt.ylabel(arg[1]);plt.xlabel(arg[2]);plt.show()

def cnsp(data, stepsize=1e-7, glob=1): #consecutive split
    if glob==1:
        rs=np.split(np.argsort(data), np.where(np.diff(sorted(data)) > stepsize)[0]+1)
    elif glob==0:
        rs=np.split(list(range(len(data))), np.where(np.diff(data) > stepsize)[0]+1)
    return rs

ql=Spectrum.objects.all()
Xa=scal([i.y().tolist() for i in ql])
ids=[i.nir_profile_id for i in ql.all()]
titles= [i.origin for i in ql.all()]

mt=Match.objects.last()
sm=StaticModel.objects.first()

ob=sm.add_match(mt)