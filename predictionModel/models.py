from django.db import models
from core.models import Spectrum
from spectraModelling.models import wavelength_length, x_poly, fft_sampling
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np

class PcaModel(models.Model):
    score = models.FloatField(blank=True, null=True)
    order = models.IntegerField(default = 2)
    component = models.TextField(blank=True, null=True)
    calibration = models.ManyToManyField(Spectrum)
    
    def __str__(self):
        fname=self.calibration.all()[0].origin.split(' ')[0]
        if self.calibration.count()> 1:
            origin_list=list(set([i.origin.split(' ')[0] for i in self.calibration.all()]))
            if len(origin_list) == 2:
                fname= "%s and %s, score: %s" % (origin_list[0], origin_list[1], "{:0.2f}".format(self.score))
            elif len(origin_list) > 2:
                fname= "%s, %s and %d others, score: %s" % (origin_list[0], origin_list[1],self.calibration.count()-2, "{:0.2f}".format(self.score))

        else:
            fname = "%s, score: %s" % (fname, "{:0.2f}".format(self.score))
        return fname

    def comp(self):
        return np.array(eval("["+self.component+"]"))

    def obtain(self, comp, ids, score ):
        self.component=str(comp)[1:-1]
        self.score=score
        self.save()
        self.calibration.set(ids)
    
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
            pca = PCA(n_components = 2)
            pca.fit(y)
            # comp= pca.components_
            # C=comp.dot(y.T)
            C=pca.transform(y)
            S=pca.score(y)
        else:
            # test the comp on another Spectra ids
            y=self.scale_y(*ids)
            y=np.array(y)
            pca=PCA(n_components=2)
            pca.components_=self.comp()
            pca.mean_=np.mean(y,axis=0)
            # C=comp.dot(y.T)
            C=pca.transform(y)
            S=pca.score(y)
        return C, S

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
                scled.append(fft_sampling(y))
        else:
            scaled.append(i)
    
    return min_max_scal(np.array(scaled))


# Section has to be moved to test.py: 
# from predictionModel.models import PcaModel as pca
# from core.models import NirProfile, Spectrum
# q=Spectrum.objects.filter(nir_profile=4)
# p=pca.objects.first()
# p.obtain()