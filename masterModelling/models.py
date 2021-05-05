from django.db import models
from django.db.models.signals import post_save
from core.models import Spectrum
import numpy as np
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scale_x
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

class StaticModel(models.Model):
    title=models.CharField(max_length=60)
    spectra=models.TextField(blank=True, null=True)
    profile=models.TextField(blank=True, null=True)
    count=models.IntegerField(blank=True, null=True)
    score=models.IntegerField(blank=True, null=True)
    n_comp=models.IntegerField(blank=True, null=True)
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
        mn,st=X.mean(),X.std()
        # find if preprocessed:
        prep=self.get_prep()
        if prep: # incase preprocessed
            gp=prep.predict(np.c_[mn,st*3])[0]
            # scale along y of its group
            stat=self.get_stat()
            gm=stat[gp]['mean']
            gs=stat[gp]['std']
            Xy=(Xx-gm)/gs
        else:
            Xy=X.reshape(1,-1)

        #apply the model:
        mod=self.get_mod()
        # print(Xy.shape,'-'*40)
        # mod.mean_=np.array(mod.mean_.tolist()+[mn])
        # print(mod.mean_.shape)
        trans=mod.transform(Xy).T
        
        if update: # incase we want to update mean_ & trans in the model for update
            tr=np.array(eval(self.trans))
            mod.mean_=np.array(mod.mean_.tolist()+[mn])
            print('sm tr:',trans.shape,'lg tr:',tr.shape,mod.components_.shape)
            result=np.c_[tr.T,trans].T
        else:
            print(trans.shape)
            result=trans 
        return result

    def get_prep(self):
        prep=self.prep()
        prep_obj =None
        if 'kmean' in prep:
            prep_obj = dict2obj(prep['kmean'],KMeans())
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
    
    def add_last(self,id,origin,profile,X):
        sp=eval(self.spectra)
        pr=eval(self.profile)
        color = self.find_color(origin,pr['color_set'])
        #update spectra:
        sp['ids']=sp['ids']+[id]
        sp['titles']=sp['titles']+[origin]
        sp['colors']=sp['colors']+list(color.values())
        sp['color_titles']=sp['color_titles']+list(color.keys())
        self.spectra=sp
        #upddate profile
        pr['ids']=pr['ids']+[profile.id if profile else None]
        self.profile=pr
        print(len(pr['ids']))
        #update the model:
        trans=self.transform(X,update=True)
        # print(trans.shape,'-'*40,mod.mean_.shape,mod.components_[-1].shape)
        # trans=np.array(eval(self.trans))
        self.trans=trans.tolist()
        # mod_di=mod.__dict__
        # mod_s={i:(mod_di[i].tolist() if type(mod_di[i]) is np.ndarray else mod_di[i]) for i in mod_di}
        # am=eval(self.applied_model)
        # print(am.keys(),'pca' in am)
        # if 'pca' in am:
        #     am['pca']=mod_s
        print('%s model for (%s) updated successfully' % (self.title,origin))
        # self.applied_model=am
        self.save()

    def find_color(self,origin,color_set):
        origin = origin.lower()
        color= None
        for i in color_set:
            if i in origin and not color:
                color={i:'rgba(%s)' % color_set[i]}
        if not color:
            color={'other':'rgba(%s)' % color_set['other']}
        return color


    class Meta:
        verbose_name = 'Static Model'
        verbose_name_plural = "Static Models"


class IngredientsModel(models.Model):
    title=models.CharField(max_length=60)
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


def dict2obj(dct,obj):
    for i in dct:
        obj=obj
        val=dct[i]
        if type(val) is list:
            exec("obj."+i+"=np.array(val)")
        else:
            exec("obj."+i+"=val")
    return obj

# auto update StaticModel whenever Spectrum created.
def StaticModel_receiver(sender, instance, created, *args, **kwargs):
    
    if created and instance.y_axis:
        id=instance.id
        origin=instance.origin
        profile=instance.nir_profile 
        X=instance.y()
        # mn=X.mean();st=X.std()
        for sm in StaticModel.objects.all():
            sm.add_last(id,origin,profile,X)
            print(sm.title+': add(%s) successfully' % origin)

post_save.connect(StaticModel_receiver, sender=Spectrum)