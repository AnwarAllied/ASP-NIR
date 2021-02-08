from django.db import models
from core.models import Spectrum
from spectraModelling.models import wavelength_length, x_poly, fft_sampling
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np
from sklearn.cross_decomposition import PLSRegression


class PlsModel(models.Model):
    component = models.TextField(blank=True, null=True, default=2)
    calibration = models.ManyToManyField(Spectrum)

    def comp(self):
        return np.array(eval('['+self.component+']'))

    def obtain(self, y, *ids):
        X = self.scale_y() if not ids else self.scale_y(*ids)  # y dataset of a spectrum or of some spectra
        y = np.array(y)  # y dataset of an ingredient or of some ingredients
        pls = PLSRegression(n_components=2)
        pls.fit(X, y)
        self.component = pls.get_params(['component'])

    def scale_y(self, *ids):
        if ids:
            y = to_wavelength_length_scal([Spectrum.objects.get(id=i).y().tolist() for i in ids if Spectrum.objects.get(id=i).y().tolist()!=[]])
        else:
            y = to_wavelength_length_scal([i.y().tolist() for i in self.calibration.all() if i.y().tolist()!=[]])
        return y

    def apply(self, mode, y, *ids):  # predict the ingredients values of a spectrum or of some spectra
        if mode == 'calibration':
            X = self.scale_y() if not ids else self.scale_y(*ids)
            y = np.array(y)
            pls = PLSRegression(n_components=2)
            pls.fit(X, y)
            C = pls.score(X, y)
        else:
            X = self.scale_y(*ids)
            y = np.array(y)
            pls = PLSRegression(n_components=2)
            pls.fit(X, y)
            C = pls.score(X, y)
        return C


class PcaModel(models.Model):
    order = models.IntegerField(blank=True, null=True)
    component = models.TextField(blank=True, null=True)
    calibration = models.ManyToManyField(Spectrum)

    def comp(self):
        return np.array(eval("["+self.component+"]"))

    def obtain(self):
        y=self.scale_y()
        print('scaled to:',np.shape(y),'max:', np.max(y),'min:',np.min(y))
        # impliment PCA:
        pca = PCA(n_components = 2)
        pca.fit(y)
        self.order=pca.get_params()['n_components']
        self.component=str(pca.components_.tolist())[1:-1]
        # reduced = pca.transform(data_rescaled)
    
    def scale_y(self,*ids):
        if ids:
            y=to_wavelength_length_scal([Spectrum.objects.get(id=i).y().tolist() for i in ids])
        else:
            y=to_wavelength_length_scal([i.y().tolist() for i in self.calibration.all()])
        return y
    
    def apply(self,mode,*ids):
        if mode=='calibration':
            # new PCA of the selected Spectra
            # ids=[i.id for i in self.calibration.all()]
            y=self.scale_y() if not ids else self.scale_y(*ids)
            y=np.array(y)
            pca = PCA(n_components=2)
            pca.fit(y)
            comp= pca.components_
            C=comp.dot(y.T)
        else:
            # test the comp on another Spectra ids
            y=self.scale_y(*ids)
            y=np.array(y)
            comp=self.components_
            C=comp.dot(y.T)
        return C



def min_max_scal(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)

def to_wavelength_length_scal(y):
    scaled=[]
    for i in y:
        l=len(i)
        if l != wavelength_length:
            df=l-wavelength_length
            if df>0:
                x=np.round(np.linspace(0,l-1,wavelength_length)).astype(int)
                scaled.append([i[a] for a in x])
            else:
                scaled.append(fft_sampling(y))
        else:
            scaled.append(i)
    
    return min_max_scal(np.array(scaled))