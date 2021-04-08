from django.test import TestCase

# from predictionModel.models import PcaModel, to_wavelength_length_scale as scal
from predictionModel.models import PlsModel
from core.models import NirProfile, Spectrum
from preprocessingFilters.models import SgFilter
from scipy.signal import savgol_filter
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
# from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA

# exec(open('preprocessingFilters/tests.py','r').read())

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

# def min_max_scal(data):
#     scaler = MinMaxScaler()
#     return scaler.fit_transform(data)

def savgol_average(x, w, p):
    return savgol_filter(x, w, p, deriv=2,mode='mirror')

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

q1=Spectrum.objects.filter(nir_profile=10)
q2=Spectrum.objects.filter(nir_profile=11)
X=np.array([i.y().tolist() for i in q1.all()] )
V=np.array([i.y().tolist() for i in q2.all()] )
lx=np.array([float(re.findall('\d[\d\.]*',i.origin)[0]) for i in q1.all()])
lv=np.array([float(re.findall('\d[\d\.]*',i.origin)[0]) for i in q2.all()])

# Xs=savgol_average(X, 13, 2)
# Xs.shape
# Xs.mean

# Sg=SgFilter(polyorder=2)
# Sg.obtain(ids=[8])

# Ss=Sg.y()
# Ss.shape
# Ss.mean
pls=PLSRegression(n_components=10)
pls.fit(X,lx)
pls.score(V,lv)

Xs=savgol_average(X, 35, 2)
Vs=savgol_average(V, 35, 2)
pls2=PLSRegression(n_components=10)
pls2.fit(Xs,lx)
pls2.score(Vs,lv)
