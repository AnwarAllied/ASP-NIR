# from django.test import TestCase

# from masterModelling.models import StaticModel, IngredientsModel
# from .models import to_wavelength_length_scale as scal
from spectraModelling.models import wavelength_length
from core.models import NirProfile, Spectrum
from chartjs.colors import next_color
from matplotlib import pyplot as plt
import numpy as np
# import pandas as pd
import re
# from sklearn.linear_model import LinearRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
# from sklearn.preprocessing import MinMaxScaler
# from sklearn.decomposition import PCA
# from scipy.signal import savgol_filter
# from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA
# from sklearn.cluster import KMeans


# exec(open('predictionModel/mng.py','r').read())

color_set={ 'wheat':'255, 165, 0',
            'wheatSG':'250, 175, 10',
            'durum':'35, 125, 235',
            'narcotic':'190,190,190',
            'tomato':'216, 31, 42',
            'garlic':'201,35,212',
            'grape':'0, 176, 24',
            'fruit':'150, 106, 54',
            'other': '170 170 170' }
narcotic_set=['phenacetin','lidocaine','levamisole','cocaine','caffeine','benzocaine']
fruit_set = ['apple','Apple','banana','Pear']

def obtain_pca_meat(pc):

    st=['sp_ids', 'sp_titles', 'sp_colors', 'co_titles', 'pr_ids']
    data= get_spc_meta()
    pr_titleset=list(set(data['pr_titles']))
    # pc=PcaModel.objects.all() if not pca else [pca]
    for obj in pc:
        dt={i:data[i] for i in st}
        ids=dt['sp_ids']
        pc_ids=[i.id for i in obj.calibration.all()]
        idx=[ids.index(i) for i in pc_ids]
        for j in st:
            dt[j]=[dt[j][i] for i in idx]
        
        dt['count']=len(pc_ids)
        dt['colorset']={i:data['colorset'][i] for i in data['colorset'] if i in dt['co_titles']}
        dt['pr_titles']=[NirProfile.objects.get(id=i).title for i in set(dt['pr_ids']) if i]
        obj.meta=dt
        obj.save()
        print('meat for pca:',obj.id)

def get_title_color(titles):
    # to get fast meta for view unsaved pcaModel:
    return obtain_colors(titles,color_set,narcotic_set)


def get_spc_meta():
    # to_remove_from_query:
    ql=Spectrum.objects.all() #.exclude(origin__contains=remove[0])
    # for i in remove:
    #     ql=ql.exclude(origin__contains=i)

    # Xa=scale_x([i.y().tolist() for i in ql])
    sp_ids=[i.id for i in ql.all()]
    sp_titles= [i.origin for i in ql.all()]
    sp_colors,co_titles, colorset=obtain_colors(sp_titles,color_set,narcotic_set)
    pid=[i.nir_profile_id for i in ql.all()]
    pr={'pr_ids':pid,'pr_titles':[NirProfile.objects.get(id=i).title for i in set(pid) if i]}
    out={ 'sp_ids':sp_ids, 'sp_titles':sp_titles, 'sp_colors':sp_colors,
    'co_titles':co_titles, 'colorset':colorset, 'pr_ids': pr['pr_ids'], 'pr_titles':pr['pr_titles']}
    return out

def obtain_colors(titles,color_set,narcotic,fruit=fruit_set):
    s1=str(titles).lower()
    s2=re.sub('[^\w ]+','',s1)
    s3=re.sub(r'\d+|\b\w{1,2}\b','',s2)
    s4=re.sub('brix|protein|moisture|data|test|validation|calibration|asp|italian|roma','',s3)
    s5=re.sub(' +|_+',' ',s4)
    s6=re.findall('\w{3,}',s5)
    s7={i:s6.count(i) for i in list(set(s6))}
    ls=sorted(s7.keys(), key=lambda x:s7[x],reverse=True)
    fruit=[i.lower() for i in fruit]
    gp=[]
    for i in eval(s1):
        has_origin=False
        for j in ls:
            if i in narcotic and not has_origin:
                has_origin=True
                gp.append('narcotic')
            if i in fruit and not has_origin:
                has_origin=True
                gp.append('fruit')
                # print(i, 'in narcotic')
            if j in i and not has_origin:
                has_origin=True
                gp.append(j)
            
        if not has_origin:
            gp.append('other')
    co=[]
    ti=[]
    ls=list(color_set.keys())
    color_dict={}
    for i in gp:
        has_origin=False
        for j in ls:
            if j in i and not has_origin:
                has_origin=True
                co.append('rgba(%s, 1)' % color_set[j])
                ti.append(j)
                color_dict.update({j:color_set[j]})
        if not has_origin:
            new_color=str(tuple(next(next_color())))
            co.append('rgba%s' %new_color)
            ti.append(i)
            color_set.update({i:new_color[1:-1]})
            color_dict.update({i:new_color[1:-1]})
    return co, ti, color_dict


def scale_x(y):
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
