from django.db import models
from core.models import Spectrum
from spectraModelling.models import wavelength_length, x_poly, fft_sampling
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error as MSE
from preprocessingFilters.models import SgFilter
from re import findall

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
    y_pred = models.TextField(blank=True, null=True)
    preprocessed = models.CharField(max_length=20, blank=True, null=True)
    calibration = models.ManyToManyField(Spectrum)

    def __str__(self):
        fname=self.calibration.all()[0].origin.split(' ')[0]+", score: "+"{:0.2f}".format(self.score)+", mse: " + "{:0.2f}".format(self.mse) + ", comp.: "+str(self.order)
        if self.calibration.count()> 1:
            origin_list=list(set([i.origin.split(' ')[0] for i in self.calibration.all()]))
            if len(origin_list) == 2:
                fname= "%s and %s, score: %s, mse: %s" % (origin_list[0], origin_list[1], "{:0.2f}".format(self.score), "{:0.2f}".format(self.mse))
            elif len(origin_list) > 2:
                fname= "%s, %s and %d others, score: %s, mse: %s" % (origin_list[0], origin_list[1],self.calibration.count()-2, "{:0.2f}".format(self.score), "{:0.2f}".format(self.mse))
        else:
            fname = "%s, score: %s, score: %s" % (fname, "{:0.2f}".format(self.score), "{:0.2f}".format(self.mse))
        fname= fname + ' - SG filtred' if self.preprocessed else fname
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

    def ypred(self):
        return np.array(eval("["+self.y_pred+"]"))

    def obtain(self, ids, trans, components, score, mse, xrots, xmean, ymean, plscoef, xstd, ypred, preprocessed):
        self.score = score
        self.mse = mse
        self.order= components
        self.transform = str(trans)[1:-1]
        self.x_rotations = str(xrots)[1:-1]
        self.x_mean = str(xmean)[1:-1]
        self.y_mean = str(ymean)[1:-1]
        self.coef = str(plscoef)[1:-1]
        self.x_std = str(xstd)[1:-1]
        self.y_pred = str(ypred)[1:-1]
        self.preprocessed=preprocessed
        self.save()
        self.calibration.set(ids)

    def scale_y(self,*ids):
        if ids:
            y=to_wavelength_length_scale(np.array([Spectrum.objects.get(id=i).y().tolist() for i in sorted(ids)]))
        else:
            y=to_wavelength_length_scale(np.array([i.y().tolist() for i in self.calibration.all().order_by('id')]))
        return y
    
    def get_calibration_ids(self):
        return [i.id for i in self.calibration.all()]

    def get_y_train(self, spectra=None):
        # if spectra:
        return np.array([float(findall('\d[\d\.]*',i.origin)[0]) if findall('\d',i.origin) else None for i in (spectra if spectra else self.calibration.all())])
        # else:
        #     return np.[float(findall('\d[\d\.]*',i.origin)[0]) for i in self.calibration.all()]

    def apply(self, mode, components, *ids, **kwargs):
        if mode == 'calibration':
            if ids:
                spectra = [Spectrum.objects.get(id=i) for i in sorted(ids)]
            else:
                spectra = [Spectrum.objects.all()]
            spectra_filter = [i for i in spectra if findall('\d[\d\.]*',i.origin)]
            # print('spectra_filter:', len(spectra_filter),'from:',len(spectra))
            ids_spec = [i.id for i in spectra_filter]
            if 'SgFilter' in str(type(kwargs['model'])):
                X_train = kwargs['model'].y()
                Y_train = kwargs['model'].ingr()
            else:
                X_train = self.scale_y(*ids_spec)
                Y_train = self.get_y_train(spectra_filter)
            
            pls = PLSRegression(n_components=components)
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
            y_comp = Y_train
            # print(x_mean[0],x_mean[-1],y_mean[0],y_mean[-1],x_std[0],x_std[-1],coef.shape,coef[0],coef[-1],trans.shape,trans[0,0],trans[5,5],y_pred[0],y_pred[-1,],x_rotations.shape,x_rotations[0,0],x_rotations[5,5])
            # print('calibration-- score: %s, mse: %s' % (score, mse))
        else:
            # if ids:
            # print(ids,'\n',self.preprocessed)
            if self.preprocessed:
                SG=SgFilter.objects.get(id=ids[0])#self.preprocessed.split(',')[1])
                spectra_testing = SG.nirprofile.first().spectrum_set.all()#[Spectrum.objects.get(id=i) for i in ids]
                ids = [i.id for i in spectra_testing]
                testing_set_scaled = SG.y()
                y_true=SG.ingr()
            else:
                spectra_testing = [Spectrum.objects.get(id=i) for i in ids]
                testing_set = [i.y() for i in spectra_testing]
                testing_set_scaled = to_wavelength_length_scale(testing_set)
                y_true=self.get_y_train(spectra_testing)
            components = self.order
            pls = PLSRegression(n_components=components)
            pls.x_rotations_ = self.xrots()
            pls.x_mean_ = self.xmean()
            pls.x_std_ = self.xstd()
            trans = pls.transform(testing_set_scaled)  # transform(x) needs x_mean_, x_std_ and x_rotations_
            pls.coef_ = self.pcoef()
            pls.y_mean_ = self.ymean()
            y_pred = pls.predict(testing_set_scaled)  # predict(x) needs x_mean_, y_mean_, coef_
            y_comp = np.array([y_true[i] if y_true[i] else y_pred[i][0] for i in range(len(y_true))])
            score = pls.score(testing_set_scaled, y_comp)
            # print('score:',score)
            # print('y_pred:',y_pred)
            # print('origin:',[i.origin for i in spectra_testing])
            mse = None
            x_rotations = pls.x_rotations_
            x_mean = pls.x_mean_
            y_mean = pls.y_mean_
            coef = pls.coef_
            x_std = pls.x_std_
            ids_spec = ids
            # print('testing-- y_pred:%s' % (y_pred))
        return trans, components, score, mse, x_rotations, x_mean, y_mean, coef, x_std, y_pred, ids_spec, y_comp


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
            y=to_wavelength_length_scale([Spectrum.objects.get(id=i).y().tolist() for i in ids])
        else:
            y=to_wavelength_length_scale([i.y().tolist() for i in self.calibration.all()])
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

def min_max_scale(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)

def to_wavelength_length_scale(y):
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
    
    return np.array(scaled)

def normalize_y(y):
    data=to_wavelength_length_scale(y)
    return min_max_scale(data)


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