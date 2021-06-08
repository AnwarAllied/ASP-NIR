import re

from chartjs.colors import next_color
from django.db import models
from django.db.models.signals import post_save
from core.models import Spectrum, NirProfile
import numpy as np
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scale_x
from sklearn.decomposition import PCA
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
        prep=self.prep()
        return prep['stat']

    def transform(self,X,update=False):
        # scale along x:
        Xx=scale_x([X])
        # find its mean&std gruop:
        prep=self.get_prep()
        if prep: # incase preprocessed
            mn,st=X.mean(),X.std()
            gp=prep.predict(np.c_[mn,st*3])[0]
            # scale along y of its group
            stat=self.get_stat()
            gm=stat[gp]['mean']
            gs=stat[gp]['std']
            Xy=(Xx-gm)/gs
        else:
            Xy=Xx.reshape(1,-1)

        #apply the model:
        mod=self.get_mod()
        trans = mod.transform(Xy).T
        if update:  # incase we want to update & trans in the model for update
            tr = np.array(eval(self.trans))
            # mod.mean_=np.array(mod.mean_.tolist()+[mn])
            result = np.c_[tr.T, trans].T
        else:
            result = trans
        return result

    def get_prep(self):
        prep = self.prep()
        prep_obj = None
        if 'kmean' in prep:
            prep_obj = dict2obj(prep['kmean'], KMeans())
        return prep_obj

    def get_mod(self):
        mod=self.mod()
        mod_obj=None
        # kys=mod.keys()
        if 'pca' in mod:
            mod_obj = dict2obj(mod['pca'],PCA())
        return mod_obj

    def color(self):
        sp=eval(self.spectra)
        return sp['colors'],sp['color_titles']

    def add_last(self, id, origin, profile, X):
        sp = eval(self.spectra)
        pr = eval(self.profile)
        color = self.find_color(origin, pr['color_set'])
        # update spectra:
        sp['ids'] = sp['ids'] + [id]
        sp['titles'] = sp['titles'] + [origin]
        sp['colors'] = sp['colors'] + list(color.values())
        sp['color_titles'] = sp['color_titles'] + list(color.keys())
        self.spectra = sp
        self.count = self.count + 1
        # upddate profile
        pr['ids'] = pr['ids'] + [profile.id if profile else None]
        self.profile = pr
        # update the trans:
        trans = self.transform(X, update=True)
        self.trans = trans.tolist()
        print('%s model for (%s) updated successfully' % (self.title, origin))
        # self.applied_model=am
        self.save()

    def add_match(self, obj):
            sp = eval(self.spectra)
            pr = eval(self.profile)
            color = {'unknown': 'grba(77, 77, 77, 1)'}
            # update spectra:
            sp['ids'] = sp['ids'] + [obj.pk]
            sp['titles'] = sp['titles'] + ['unknown']
            sp['colors'] = sp['colors'] + list(color.values())
            sp['color_titles'] = sp['color_titles'] + list(color.keys())
            self.spectra = str(sp)
            self.count = self.count + 1
            # upddate profile
            pr['ids'] = pr['ids'] + [None]
            self.profile = str(pr)
            # update the trans:
            trans = self.transform(obj.y(), update=True)
            self.trans = str(trans.tolist())
            return self

    def find_color(self, origin, color_set):
            origin = origin.lower()
            color = None
            for i in color_set:
                if i in origin and not color:
                    color = {i: 'rgba(%s)' % color_set[i]}
            if not color:
                color = {'other': 'rgba(%s)' % color_set['other']}
            return color


    def pred_pca_match(self,pca_id,spec_pca_ids,spectrum):
        pred_pca = PcaModel.objects.get(id=pca_id)
        pr = eval(self.profile)
        sp = eval(self.spectra)

        spec_pca_spectra=[Spectrum.objects.get(id=i) for i in spec_pca_ids if i]
        nir_ids=[i.nir_profile_id for i in spec_pca_spectra]

        # update profile
        pr['ids']=nir_ids+[spectrum.nir_profile_id if spectrum.nir_profile_id else None]
        print('profile-ids:',pr['ids'])
        pr['titles']=[i.title for i in [NirProfile.objects.get(id=j) for j in set(pr['ids']) if j]]
        self.profile = str(pr)

        # update spectra
        sp['ids']=spec_pca_ids+[spectrum.pk if spectrum.pk else None]  #
        titles=[i.origin for i in spec_pca_spectra] + [spectrum.origin]
        sp['titles']=titles
        co,ti,co_di=obtain_colors(titles)
        sp['colors'] = co
        sp['color_titles'] = ti
        self.spectra = str(sp)

        # update the trans:
        Xy = spectrum.y()
        Xy=scale_x([Xy]).tolist()

        # print('Xy:',Xy)
        X=[scale_x([i.y()])[0].tolist() for i in spec_pca_spectra]
        # print('shape:',np.shape(Xy),np.shape(X))
        Xn=X+Xy
        # print('X num:',len(X))
        pca=PCA(n_components=2)
        pca.fit(Xn)
        trans=pca.transform(Xn)
        self.trans = str(trans.tolist())

        #update other attributes
        self.title = pred_pca.__str__()
        self.count = len(spec_pca_ids) + 1
        return self



    class Meta:
        verbose_name = 'Static Model'
        verbose_name_plural = "Static Models"


def obtain_colors(titles):
    color_set = {'wheat': '255, 165, 0', 'durum': '235, 97, 35', 'narcotic': '120,120,120', 'tomato': '216, 31, 42',
                 'garlic': '128,128,128', 'grape': '0, 176, 24', 'other': '241 170 170'}
    # sp=kwargs['spectra']
    # s1=str(sp['titles']).lower()
    s1 = str(titles).lower()
    s2 = re.sub('[^\w ]+', '', s1)
    s3 = re.sub(r'\d+|\b\w{1,2}\b', '', s2)
    s4 = re.sub('brix|protein|moisture|data|test|validation|calibration|asp', '', s3)
    s5 = re.sub(' +', ' ', s4)
    s6 = re.findall('\w{3,}', s5)
    s7 = {s6.count(i): i for i in list(set(s6))}
    ls = sorted(s7.keys(), reverse=True)
    gp = []
    for i in eval(s1):
        has_origin = False
        for j in ls:
            if s7[j] in i and not has_origin:
                has_origin = True
                gp.append(s7[j])
        if not has_origin:
            gp.append('other')
    co = []
    ti = []
    ls = list(color_set.keys())
    color_dict = {}
    for i in gp:
        has_origin = False
        for j in ls:
            if j in i and not has_origin:
                has_origin = True
                co.append('rgba(%s, 1)' % color_set[j])
                ti.append(j)
                color_dict.update({j: color_set[j]})
        if not has_origin:
            new_color = str(tuple(next(next_color())))
            co.append('rgba%s' % new_color)
            ti.append(i)
            color_set.update({i: new_color[1:-1]})
            color_dict.update({i: new_color[1:-1]})
    return co, ti, color_dict




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


def dict2obj(dct, obj):
    for i in dct:
        obj = obj
        val = dct[i]
        if type(val) is list:
            exec("obj." + i + "=np.array(val)")
        else:
            exec("obj." + i + "=val")
    return obj


# auto update StaticModel whenever Spectrum created.
# def StaticModel_receiver(sender, instance, created, *args, **kwargs):
#     if created and instance.y_axis:
#         id = instance.id
#         origin = instance.origin
#         profile = instance.nir_profile
#         X = instance.y()
#         # mn=X.mean();st=X.std()
#         for sm in StaticModel.objects.all():
#             sm.add_last(id, origin, profile, X)
#             print(sm.title + ': add(%s) successfully' % origin)
#
#
# post_save.connect(StaticModel_receiver, sender=Spectrum)