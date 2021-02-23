from django.db import models
from core.models import Spectrum
from spectraModelling.models import wavelength_length, x_poly, fft_sampling
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error as MSE

class PlsModel(models.Model):
    order = models.IntegerField(default=2)
    score = models.FloatField(blank=True, null=True)
    mse = models.FloatField(blank=True, null=True)
    x_rotations = models.TextField(blank=True, null=True)
    x_std = models.TextField(blank=True, null=True)
    x_mean = models.TextField(blank=True, null=True)
    y_mean = models.TextField(blank=True, null=True)
    coef = models.TextField(blank=True, null=True)
    transform = models.TextField(blank=True, null=True)
    calibration = models.ManyToManyField(Spectrum)

    def __str__(self):
        fname=self.calibration.all()[0].origin.split(' ')[0]+", score: "+"{:0.2f}".format(self.score)+", mse: " + "{:0.2f}".format(self.mse)
        if self.calibration.count()> 1:
            origin_list=list(set([i.origin.split(' ')[0] for i in self.calibration.all()]))
            if len(origin_list) == 2:
                fname= "%s and %s, score: %s, mse: %s" % (origin_list[0], origin_list[1], "{:0.2f}".format(self.score), "{:0.2f}".format(self.mse))
            elif len(origin_list) > 2:
                fname= "%s, %s and %d others, score: %s, mse: %s" % (origin_list[0], origin_list[1],self.calibration.count()-2, "{:0.2f}".format(self.score), "{:0.2f}".format(self.mse))
        else:
            fname = "%s, score: %s, score: %s" % (fname, "{:0.2f}".format(self.score), "{:0.2f}".format(self.mse))
        return fname

    def trans(self):
        return np.array(eval("["+self.transform+"]"))

    def xrots(self):
        return np.array(eval("["+self.x_rotations+"]"))

    def xmean(self):
        return np.array(eval("["+self.x_mean+"]"))

    def ymean(self):
        return np.array(eval("["+self.y_mean+"]"))

    def xstd(self):
        return np.array(eval("["+self.x_std+"]"))

    def pcoef(self):
        return np.array(eval("["+self.coef+"]"))

    def obtain(self, ids, trans, score, mse, xrots, xmean, ymean, plscoef, xstd):
        self.score = score
        self.mse = mse
        self.transform = str(trans)[1:-1]
        self.x_rotations = str(xrots)[1:-1]
        self.x_mean = str(xmean)[1:-1]
        self.y_mean = str(ymean)[1:-1]
        self.coef = str(plscoef)[1:-1]
        self.x_std = str(xstd)[1:-1]
        self.save()
        self.calibration.set(ids)

    def scale_y(self,*ids):
        if ids:
            y=to_wavelength_length_scal([Spectrum.objects.get(id=i).y().tolist() for i in ids])
        else:
            y=to_wavelength_length_scal([i.y().tolist() for i in self.calibration.all()])
        return y

    def isDigit(self,x):
        try:
            float(x)
            return True
        except ValueError:
            return False

    # def mod_transform(self,X, x_mean, x_std, x_rots, copy=True):
    #     X = X-x_mean
    #     X = X/x_std
    #     x_scores = np.dot(X, x_rots)
    #     return x_scores


    def apply(self, mode, *ids):
        if mode == 'calibration':
            if ids:
                spectra = [Spectrum.objects.get(id=i) for i in ids]
            else:
                spectra = [Spectrum.objects.all()]
            spectra_filter = [i for i in spectra for j in i.origin.split() if self.isDigit(j)==True]
            ids_spec = [i.id for i in spectra_filter]
            X_train = self.scale_y(*ids_spec).tolist()
            Y_train = [float(j) for i in spectra_filter for j in i.origin.split() if self.isDigit(j)==True]
            pls = PLSRegression(n_components=2)
            pls.fit(X_train, Y_train)
            trans = pls.transform(X_train)
            score = pls.score(X_train, Y_train)
            y_pred = pls.predict(X_train)
            mse = MSE(Y_train, y_pred)
            x_rotations = pls.x_rotations_
            x_mean = pls.x_mean_
            y_mean = pls.y_mean_
            coef = pls.coef_
            x_std = pls.x_std_
            print('calibration-- score: %s, mse: %s' % (score, mse))
        else:
            if ids:
                spectra = [Spectrum.objects.get(id=i) for i in ids]
                spectra_filter = [i for i in spectra for j in i.origin.split() if self.isDigit(j) == True]
                ids_spec = [i.id for i in spectra_filter]
                X = self.scale_y(*ids_spec).tolist()
                # for testing
                # y = [float(j) for i in spectra_filter for j in i.origin.split() if self.isDigit(j) == True]
                pls = PLSRegression(n_components=2)
                pls.x_rotations_ = self.xrots()
                pls.x_mean_ = self.xmean()
                pls.x_std_ = self.xstd()
                trans = pls.transform(X)  # transform(x) needs x_mean_, x_std_ and x_rotations_
                pls.coef_ = self.pcoef()
                pls.y_mean_ = self.ymean()
                y_pred = pls.predict(X)  # predict(x) needs x_mean_, y_mean_, coef_
                score = self.score
                mse = self.mse
                x_rotations = pls.x_rotations_
                x_mean = pls.x_mean_
                y_mean = pls.y_mean_
                coef = pls.coef_
                x_std = pls.x_std_
                print('testing-- y_pred:%s' % (y_pred))
        return trans, score, mse, x_rotations, x_mean, y_mean, coef, x_std


class PcaModel(models.Model):
    score = models.FloatField(blank=True, null=True)
    order = models.IntegerField(default = 2)
    component = models.TextField(blank=True, null=True)
    transform = models.TextField(blank=True, null=True)
    calibration = models.ManyToManyField(Spectrum) #on_delete=DO_NOTHING
    
    def __str__(self):
        fname=self.calibration.all()[0].origin.split(' ')[0]+", score: "+"{:0.2f}".format(self.score)
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

    def trans(self):
        return np.array(eval("["+self.transform+"]"))

    def obtain(self, comp, ids, trans, score ):
        self.component=str(comp)[1:-1]
        self.score=score
        self.transform=str(trans)[1:-1]
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
            comp= pca.components_
            trans=pca.transform(y) # OR trans=comp.dot(y.T).T
            try: # incase len(y)<=2:
                score = pca.score(y)
            except ValueError:
                score = 00
            print('the calibration score:',score)
        else:
            # test the comp on another Spectra ids
            y=self.scale_y(*ids)
            y=np.array(y)
            pca=PCA(n_components = 2)
            pca.n_components_=2
            pca.components_=self.comp()
            pca.mean_=np.mean(y,axis=0)
            comp = self.comp()
            trans=pca.transform(y)
            score = 00
            # sc=PCA(n_components = 2)
            # sc.fit(y)
            # pca.explained_variance_=sc.explained_variance_
            # pca.singular_values_=sc.singular_values_
            # pca.noise_variance_=sc.noise_variance_
            # score=pca.score(y)
            # print('the testing score:',score)
        return comp, trans, score

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
                scaled.append(fft_sampling(i))
        else:
            scaled.append(i)
    
    return min_max_scal(np.array(scaled))


# Section has to be moved to test.py: 
# from predictionModel.models import PcaModel
# from core.models import NirProfile, Spectrum
# import numpy as np
# q=Spectrum.objects.filter(nir_profile=4)
# y=np.array([i.y().tolist() for i in q.all()])
# ids=[73,66,61,35,31,2,1]
# y1=[Spectrum.objects.get(id=i).y().tolist() for i in ids]
# p=PcaModel()
# p.scale_y(*ids)