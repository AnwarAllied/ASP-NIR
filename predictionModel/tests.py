from django.test import TestCase

# Section has to be moved to test.py: 
from predictionModel.models import PcaModel, to_wavelength_length_scal as scal
from core.models import NirProfile, Spectrum
from matplotlib import pyplot as plt
import numpy as np
import re
# from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

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


q=Spectrum.objects.filter(nir_profile=4)
X=min_max_scal(np.array([i.y().tolist() for i in q.all()]))
x_axis=np.reshape(q.first().x(),(228,1))
y=np.array([float(re.sub('[^\d\.]+','',i.origin)) for i in q.all()])
X2s=np.array(scal([i.y().tolist() for i in q2.all()]))
# ids=[73,66,61,35,31,2,1]
# y1=[Spectrum.objects.get(id=i).y().tolist() for i in ids]
# p=PcaModel()
# p.scale_y(*ids)

#PCA:
pca = PCA(n_components=15)
pca.fit(X)
C1=pca.components_  # principle component
# C=P.dot(X.T)      # Coefficient
# D=pca.transform(Xsg)
# Pc=C.dot(Xsg)
# Pd=D.T.dot(Xsg)
# _=[plt.text(a, b, str(c[0])) for a,b,c in zip(C[0,:],C[1,:],b)];_=plt.plot(C[0,:],C[1,:],'ro');plt.title('1st Vs 2nd Component');plt.ylabel('2ed component');plt.xlabel('1st component');plt.show()

# MSE measuers
# er=np.zeros(l-15)
# for i in range(1,l-20):
#     pls2 = PLSRegression(n_components=i);
#     pls2.fit(Xsm, y);
#     y_p = pls2.predict(Xsm)
#     er[i-1]=sum((y.reshape(l,1)-y_p)**2)/l

# _=plt.plot(er.T);plt.ylabel('MSE');plt.xlabel('Component');plt.show()

# PLS analysis:
pls2 = PLSRegression(n_components=15)
pls2.fit(X, y)
y_p = pls2.predict(X)
T=pls2.x_scores_   #(54, 10) = pls2.transform(X)
U=pls2.y_scores_   #(54, 10)
W=pls2.x_weights_  #(228, 10)
C2=pls2.y_weights_   #(1, 10)
P=pls2.x_loadings_   #(228, 10)
Q=pls2.y_loadings_   #(1, 10)
y_=X.dot(pls2.coef_)*5+18

# for prediction:
pl.x_mean_=pls2.x_mean_; pl.x_std_=pls2.x_std_; pl.coef_=pls2.coef_; pl.y_mean_=pls2.y_mean_

# ['x_scores_','y_scores_','x_weights_','y_weights_','x_loadings_','y_loadings_']

# then for transform:
for i in ['x_rotations_','y_rotations_']:
    exec('pl.'+i+' = pls2.'+i)

# plt.plot(y,'ro');plt.plot(y_p,'ro', color='b');plt.ylabel('Protein (%)');plt.xlabel('samples');plt.show()
# exec(open('predictionModel/tests.py','r').read())


# Apply rPCA:
X=min_max_scal(np.array([i.y().tolist() for i in q.all()]).T).T
rpca = R_pca(X)
L, S = rpca.fit(max_iter=10000, iter_print=100)
plot((np.reshape(q.first().x(),(228,1)),X),'Grape Spectra normalized','Absorbance','Wavelength')
plot((np.reshape(q.first().x(),(228,1)),Xr),'Raw Grape Spectra','Absorbance','Wavelength')
plot((np.reshape(q.first().x(),(228,1)),L),'RPCA filtered spectra (low-rank)','Absorbance','Wavelength')
plot((np.reshape(q.first().x(),(228,1)),S),'RPCA noise (Sprase)','Absorbance','Wavelength')

cm=np.array([X[12].tolist(),L[12].tolist()])
plot((x_axis,cm),'Compare the RPCA filtered spectrum (# 12)','Absorbance','Wavelength')
