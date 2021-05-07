# from django.test import TestCase

from masterModelling.models import StaticModel, IngredientsModel
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scal
from core.models import NirProfile, Spectrum
from matplotlib import pyplot as plt
import numpy as np
# import pandas as pd
import re
# from sklearn.linear_model import LinearRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA
from sklearn.cluster import KMeans
from chartjs.colors import next_color

# exec(open('masterModelling/tests.py','r').read())

color_set={ 'wheat':'255, 165, 0',
            'durum':'35, 125, 235',
            'narcotic':'190,190,190',
            'tomato':'216, 31, 42',
            'garlic':'201,35,212',
            'grape':'0, 176, 24',
            'other': '170 170 170' }
narcotic_set=['phenacetin','lidocaine','levamisole','cocaine','caffeine','benzocaine']

def update_master_model(id):
    stat=None
    sm=StaticModel.objects.get(id=id)
    preprocess=sm.prep()
    applied_model=sm.mod()

    data_input= get_data()
    if 'pca' in applied_model:
        if not preprocess:
            ky=obtain_pca(data_input)
            stat=StaticModel.objects.filter(id=id).update(**ky)
        elif 'kmean' in preprocess:
            ky=obtain_pca_scaled(data_input)
            stat=StaticModel.objects.filter(id=id).update(**ky)
    return stat

def get_data(remove=['SG','apple','banana','Pear']):
    # to_remove_from_query:
    ql=Spectrum.objects.all().exclude(origin__contains=remove[0])
    for i in remove[1:]:
        ql=ql.exclude(origin__contains=i)

    Xa=scal([i.y().tolist() for i in ql])
    ids=[i.id for i in ql.all()]
    titles= [i.origin for i in ql.all()]
    colors,co_titles, color_set_sp=obtain_colors(titles,color_set,narcotic_set)
    pid=[i.nir_profile_id for i in ql.all()]
    profile={'ids':pid,'titles':[NirProfile.objects.get(id=i).title for i in set(pid) if i],'color_set': color_set}
    return Xa, ids, titles, colors, co_titles, color_set_sp, profile

def obtain_pca(data_input):
    Xa, ids, titles, colors, co_titles, color_set, profile=data_input
    # No preprocessing here:
    # Apply PCA:
    pca=PCA(n_components=30)
    pca.fit(Xa)
    trans=pca.transform(Xa)

    pc_di=pca.__dict__
    pca_s={i:(pc_di[i].tolist() if type(pc_di[i]) is np.ndarray else pc_di[i]) for i in pc_di}

    output={
        'title':'PCA spectra',
        'spectra':{'ids': ids,
            'titles':titles,
            'colors':colors,
            'color_titles':co_titles
            },
        'profile':profile,
        'count':len(ids),
        'score':pca.score(Xa),
        'n_comp':pca.n_components,
        'trans':trans.tolist(),
        'preprocessed':{},
        'applied_model':{'pca':pca_s},

    }
    return output

def obtain_pca_scaled(data_input):
    Xa, ids, titles, colors, co_titles, color_set, profile = data_input

    # split based on mean and std using KMean:
    #https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

    mn, st=Xa.mean(axis=1), Xa.std(axis=1)

    # find the group size (K):
    sr=np.diff(sorted((mn**2+(st*3)**2)**.5))
    df=np.diff(np.argwhere(sr>.1).astype(int),axis=0)
    t,c=[],[]
    for i in range(len(df)):
        if df[i]<5:
            c.append(df[i])
        else:
            if c:
                t.append(sum(c))
                c=[]
            else:
                t.append(df[i])
    if c:
        t.append(sum(c))
    K=len(t)

    # apply Kmean:
    kmeans = KMeans(n_clusters=K, random_state=0).fit(np.c_[mn,st*3])
    gp=kmeans.labels_
    # kmeans.predict(V)
    # plt.scatter(mn,st,c=gp,cmap='viridis');plt.colorbar();plt.show()

    #normlization each group:
    ixa=[np.argwhere(gp==i).squeeze().tolist() for i in range(K)]
    stat=[{ 'max': Xa[ixa[i]].max(),
            'min': Xa[ixa[i]].min(),
            'mean':Xa[ixa[i]].mean(),
            'std': Xa[ixa[i]].std(),
            'maxs':Xa[ixa[i]].max(axis=1).tolist(),
            'mins':Xa[ixa[i]].min(axis=1).tolist()} for i in range(K)]

    norm=[];_=[norm.extend(((Xa[np.argwhere(gp==i)].squeeze()-stat[i]['mean'])/stat[i]['std']).tolist()) for i in range(K)]

    ix=[];_=[ix.extend(np.argwhere(gp==i).tolist()) for i in range(K)]
    ix=[i[0] for i in ix]
    Xn=np.array(norm)[np.argsort(ix)].squeeze()

    # Apply PCA:
    pca=PCA(n_components=30)
    pca.fit(Xn)
    trans=pca.transform(Xn)
    km_di=kmeans.__dict__
    kmean_s={i:(km_di[i].tolist() if type(km_di[i]) is np.ndarray else km_di[i]) for i in km_di}

    pc_di=pca.__dict__
    pca_s={i:(pc_di[i].tolist() if type(pc_di[i]) is np.ndarray else pc_di[i]) for i in pc_di}

    output={
        'title':'PCA kmean-scaled spectra',
        'spectra':{'ids': ids,
            'titles':titles,
            'colors':colors,
            'color_titles':co_titles
            },
        'profile':profile,
        'count':len(ids),
        'score':pca.score(Xn),
        'n_comp':pca.n_components,
        'trans':trans.tolist(),
        'preprocessed':{
            'kmean':kmean_s,
            'stat': stat,
            'normalized': 'min_max_scal',
        },
        'applied_model':{'pca':pca_s},

    }
    return output

def obtain_colors(titles,color_set,narcotic):
    s1=str(titles).lower()
    s2=re.sub('[^\w ]+','',s1)
    s3=re.sub(r'\d+|\b\w{1,2}\b','',s2)
    s4=re.sub('brix|protein|moisture|data|test|validation|calibration|asp','',s3)
    s5=re.sub(' +|_',' ',s4)
    s6=re.findall('\w{3,}',s5)
    s7={i:s6.count(i) for i in list(set(s6))}
    ls=sorted(s7.keys(), key=lambda x:s7[x],reverse=True)
    gp=[]
    for i in eval(s1):
        has_origin=False
        for j in ls:
            if i in narcotic and not has_origin:
                has_origin=True
                gp.append('narcotic')
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



# for i in [1,2]:
#     ky=obtain_pca_scaled(Xa) if i==1 else obtain_pca(Xa)
#     StaticModel.objects.filter(id=i).update(**ky)

