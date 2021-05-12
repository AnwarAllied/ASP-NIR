from django.db import models
from django.db.models.signals import post_save
from core.models import Spectrum
import numpy as np
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scale_x
from predictionModel.mng import get_spc_meta
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
        
        if update: # incase we want to update & trans in the model for update
            tr=np.array(eval(self.trans))
            # mod.mean_=np.array(mod.mean_.tolist()+[mn])
            result=np.c_[tr.T,trans].T
        else:
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
    
    def add_last(self,id,origin,profile,X):  # for db last new created spectrum
        sp=eval(self.spectra)
        pr=eval(self.profile)
        color = self.find_color(origin,pr['color_set'])
        #update spectra:
        sp['ids']=sp['ids']+[id]
        sp['titles']=sp['titles']+[origin]
        sp['colors']=sp['colors']+list(color.values())
        sp['color_titles']=sp['color_titles']+list(color.keys())
        self.spectra=sp
        self.count=self.count+1
        #upddate profile
        pr['ids']=pr['ids']+[profile.id if profile else None]
        self.profile=pr
        #update the trans:
        trans=self.transform(X,update=True)
        self.trans=trans.tolist()
        print('%s model for (%s) updated successfully' % (self.title,origin))
        # self.applied_model=am
        self.save()

    def add_match(self,obj):    # for uploaded match spectrum
        sp=eval(self.spectra)
        pr=eval(self.profile)
        color = {'unknown': 'grba(77, 77, 77, 1)'}
        #update spectra:
        sp['ids']=sp['ids']+[obj.pk]
        sp['titles']=sp['titles']+['unknown']
        sp['colors']=sp['colors']+list(color.values())
        sp['color_titles']=sp['color_titles']+list(color.keys())
        self.spectra=str(sp)
        self.count=self.count+1
        #upddate profile
        pr['ids']=pr['ids']+[None]
        self.profile=str(pr)
        #update the trans:
        trans=self.transform(obj.y(),update=True)
        self.trans=str(trans.tolist())
        return self
    
    def set_pca(self,pca_obj,**ky):  # for view existing Pca model
        # pca_ids=[i.id for i in pca_obj.calibration.all()]
        sp=eval(self.spectra)
        pr=eval(self.profile)
        pca_m=eval(pca_obj.meta)
        #update spectra:
        # ids=sp['ids']
        # idx=[ids.index(i) for i in pca_ids]
        # sp['ids']=[ids[i] for i in idx]
        sp['ids']=pca_m['sp_ids']
        sp['titles']=pca_m['sp_titles']
        sp['colors']=pca_m['sp_colors']
        sp['color_titles']=pca_m['co_titles']
        self.spectra=str(sp)
        self.count=pca_m['count']
        #upddate profile
        pr['ids']=pca_m['pr_ids']
        self.profile=str(pr)
        #update the trans:
        trans=pca_obj.trans()
        self.trans=str(trans.tolist())
        return self

    def test_selected_pca(self,pca_obj,**ky):
        ids2=list(map(int,ky['pca_ids'].split(',')))
        ln=len(ids2)
        sp_m=get_spc_meta()
        pca_ids=[i.id for i in pca_obj.calibration.all()]+ids2
        sp=eval(self.spectra)
        pr=eval(self.profile)
        pca_m=eval(pca_obj.meta)
        #update spectra:
        idx=[sp_m['sp_ids'].index(i) for i in ids2]
        sp['ids']=pca_m['sp_ids']+[sp_m['sp_ids'][i] for i in idx]
        sp['titles']=pca_m['sp_titles']+[sp_m['sp_titles'][i] for i in idx]
        sp['colors']=pca_m['sp_colors']+[sp_m['sp_colors'][i] for i in idx]
        sp['color_titles']=pca_m['co_titles']+[sp_m['co_titles'][i] for i in idx]
        self.spectra=str(sp)
        self.count=len(sp['ids'])
        #upddate profile
        pr['ids']=pca_m['pr_ids']+[sp_m['pr_ids'][i] for i in idx]
        self.profile=str(pr)
        #update the trans:
        comp, trans, score=pca_obj.apply('test',*(pca_m['sp_ids']+ids2))
        # trans=self.transform(obj.y(),update=True)
        self.trans=str(trans.tolist())
        return self,ln

    def test_uploaded_pca(self,pca_obj,y_axis,**ky):
        sp=eval(self.spectra)
        pr=eval(self.profile)
        pca_m=eval(pca_obj.meta)
        color = {'unknown': 'grba(77, 77, 77, 1)'}
        #update spectra:
        sp['ids']=pca_m['sp_ids']+ [None]
        sp['titles']=pca_m['sp_titles'] + ['unknown']
        sp['colors']=pca_m['sp_colors'] +list(color.values())
        sp['color_titles']=pca_m['co_titles']+list(color.keys())
        self.spectra=str(sp)
        self.count=len(sp['ids'])+1
        #upddate profile
        pr['ids']=pca_m['pr_ids'] +[None]
        self.profile=str(pr)
        #update the trans:
        pca_y=np.c_[pca_obj.scale_y(*sorted(pca_m['sp_ids'])).T,np.array(y_axis)].T
        pca=PCA(n_components = pca_obj.order)
        pca.components_=pca_obj.comp()
        pca.mean_=np.mean(pca_y,axis=0)
        # pca.fit(pca_y)
        trans=pca.transform(pca_y)
        self.trans=str(trans.tolist())
        return self


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