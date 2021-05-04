from django.db import models
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scale_x
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
from sklearn.cluster import KMeans

class StaticModel(models.Model):
    title = models.CharField(max_length=60, null=True)
    spectra = models.TextField(blank=True, null=True)
    profile = models.TextField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    n_comp = models.IntegerField(blank=True, null=True)
    trans = models.TextField(blank=True, null=True)
    preprocessed = models.TextField(blank=True, null=True)
    applied_model = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def prep(self):
        # dc=eval(self.applied_model)
        # ou={i:(pc_di[i].tolist() if type(pc_di[i]) is np.ndarray else pc_di[i]) for i in pc_di}
        return eval(self.preprocessed)

    def mod(self):
        return eval(self.applied_model)

    def get_stat(self):
        prep = self.prep()
        return prep['stat']

    def transform(self, X):
        # scale along x:
        Xx = scale_x([X])
        # find its mean&std gruop:
        mn, st = X.mean(), X.std()
        prep = self.get_prep()
        gp = prep.predict(np.c_[mn, st * 3])[0]
        # scale along y of its group
        stat = self.get_stat()
        gm = stat[gp]['mean']
        gs = stat[gp]['std']
        Xy = (Xx - gm) / gs
        # apply the model:
        mod = self.get_mod()
        return mod.transform(Xy).tolist()

    def get_prep(self):
        prep = self.prep()
        prep_obj = None
        kys = list(prep.keys())
        if 'kmean' in kys:
            km_dc = prep['kmean']
            kmeans = KMeans()
            for i in km_dc:
                val = km_dc[i]
                if type(val) is list:
                    exec("kmeans." + i + "=np.array(val)")
                else:
                    exec("kmeans." + i + "=val")
            prep_obj = kmeans
        return prep_obj

    def get_mod(self):
        mod = self.mod()
        mod_obj = None
        kys = mod.keys()
        if 'pca' in kys:
            pc_dc = mod['pca']
            pca = PCA()
            for i in pc_dc:
                val = pc_dc[i]
                if type(val) is list:
                    exec("pca." + i + "=np.array(val)")
                else:
                    exec("pca." + i + "=val")
            mod_obj = pca
        return mod_obj

    class Meta:
        verbose_name = 'Static Model'
        verbose_name_plural = "Static Models"


class IngredientsModel(models.Model):
    title=models.CharField(max_length=60, null=True)
    count=models.IntegerField(blank=True, null=True)
    score=models.IntegerField(blank=True, null=True)
    n_comp=models.IntegerField(blank=True, null=True)
    origin=models.CharField(max_length=60)
    trans = models.TextField(blank=True, null=True)
    true_values=models.TextField(blank=True, null=True)
    predected_values=models.TextField(blank=True, null=True)
    preprocessed = models.TextField(blank=True, null=True)
    applied_model = models.TextField(blank=True, null=True)
    validation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def list_ingredients(self):
        # fetch all ingrediant in the database, and tell if MasterIngred. exist for each one.
        pass

    def obtain_ingred(self,ingred):
        #create MasterIngred. model for an given ingred.
        pass

    class Meta:
        verbose_name = 'Ingredients Model'
        verbose_name_plural = "Ingredients Models"