from django.db import models
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scal
from core.models import NirProfile, Spectrum
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
# from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA

# INGREDIENT_CHOICES = (
#     ('B','Brix'),
#     ('M','Moisture'),
#     ('P','Protein')
# )

class StaticModel(models.Model):
    name=models.CharField(max_length=60)
    component = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def comp(self):
        return np.array(eval("["+self.component+"]"))

    class Meta:
        verbose_name = 'Static Model'
        verbose_name_plural = "Static Models"


class IngredientsModel(models.Model):
    #mastermodel_ingre_meta
    ingredients=models.TextField(blank=True,null=True)
    ingre_model_name=models.TextField(blank=True, null=True)  # Brix

    #spec_meta
    preprocessed=models.TextField(blank=True, null=True)

    #training_meta
    origin=models.TextField(blank=True,null=True)
    count_training=models.IntegerField()
    true_ingre=models.TextField(blank=True,null=True)
    pred_ingre=models.TextField(blank=True,null=True)

    #pls_meta
    # v_count=models.IntegerField()
    # v_score=models.TextField(blank=True,null=True)
    n_components=models.TextField(blank=True,null=True)
    score=models.TextField(blank=True,null=True)
    x_rotations=models.TextField(blank=True,null=True)
    x_mean=models.TextField(blank=True,null=True)
    y_mean=models.TextField(blank=True,null=True)
    coef=models.TextField(blank=True,null=True)
    x_std=models.TextField(blank=True,null=True)
    trans=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.ingre_model_name

    class Meta:
        verbose_name = 'Ingredients Model'
        verbose_name_plural = "Ingredients Models"

    def list_ingredients(self):
        '''
        fetch all ingredients in the database,and tell
        if there's a MasterIngredient model for each ingredient
        '''
        list_ingredients=self.ingredients.split(',')
        ingredient=self.__str__()
        list_ingredients.append(ingredient)
        return list_ingredients

    def obtain_ingredient(self):
        '''
        create MasterIngredient model for a given ingredient
        '''

        all_spectra=Spectrum.objects.all()
        # scale all spectra to the same length
        Xa=scal([i.y().tolist() for i in all_spectra])
        # pre-process the data
        Xs=savgol(Xa,31,2)
        variance=np.var(Xs,axis=1)
        # divide spectra into 4 groups [very low absorbance, low, high, very high]
        cs = cnsp(variance)
        mcs = [];
        _ = [mcs.extend(i.tolist()) for i in cs[2:4]]
        lcs = [];
        _ = [lcs.extend(i.tolist()) for i in cs[4:]]
        cs = [cs[0].tolist(), cs[1].tolist(), mcs, lcs]
        svagol_stat = {'savgol': [{'max': Xs[i].max(), 'min': Xs[i].min(), 'mean': Xs[i].mean(), 'std': Xs[i].std(),
                                   'maxs': Xs[i].max(axis=1).tolist(), 'mins': Xs[i].min(axis=1).tolist()} for i in cs]}
        # normlization
        norm = [];
        _ = [norm.extend(min_max_scal(Xs[i]).tolist()) for i in cs]
        ix = [];
        _ = [ix.extend(i) for i in cs]
        Xn = np.array(norm)[np.argsort(ix)]

        # split into training set and validation set:
        origins, X, xl, V, sl = [], [], [], [], []
        ingre=self.__str__
        for spectrum_index, spectrum in enumerate(all_spectra):
            origins.append(spectrum.origin)
            if ingre not in self.list_ingredients():
                if ingre in spectrum.origin:
                    X.append(Xn[spectrum_index].tolist())
                    xl.append(float(re.findall('[\d+\.]+',origins[-1])[0]))
                    sl.append(origins[-1].split()[0].lower())
                else:
                    V.append(Xn[spectrum_index].tolist())
        X=np.array(X)
        V=np.array(V)

        #pls
        pls2=PLSRegression(n_components=15)
        pls2.fit(X,xl)
        sc=pls2.score(X,xl)




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







def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


def savgol(x, w, p):
    return savgol_filter(x, w, p, deriv=2, mode='mirror')


def min_max_scal(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)


def cnsp(data, stepsize=1e-7, glob=1): #consecutive split
    if glob==1:
        rs=np.split(np.argsort(data), np.where(np.diff(sorted(data)) > stepsize)[0]+1)
    elif glob==0:
        rs=np.split(list(range(len(data))), np.where(np.diff(data) > stepsize)[0]+1)
    return rs