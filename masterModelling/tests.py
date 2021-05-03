# from django.test import TestCase

from masterModelling.models import IngredientsModel, StaticModel 
from predictionModel.models import PlsModel, PcaModel, normalize_y , to_wavelength_length_scale as scal
from core.models import NirProfile, Spectrum
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
# from sklearn.linear_model import LinearRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSCanonical, PLSRegression, CCA
from sklearn.cluster import KMeans

# exec(open('masterModelling/tests.py','r').read())

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def savgol(x, w, p):
    return savgol_filter(x, w, p, deriv=2,mode='mirror')

def min_max_scal(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)

def plot(x,*arg):
    arg=[''] if not arg else arg
    if len(arg[0])<2:
        if type(x) is tuple:
            x1,x2=x
            plt.plot(x1,x2,arg[0]);plt.show()
        else:
            plt.plot(x,arg[0]);plt.show()
    else:
        if type(x) is tuple:
            x1,x2=x
            _=plt.plot(x1,x2.T);plt.title(arg[0]);plt.ylabel(arg[1]);plt.xlabel(arg[2]);plt.show()
        else:
            _=plt.plot(x);plt.title(arg[0]);plt.ylabel(arg[1]);plt.xlabel(arg[2]);plt.show()

def cnsp(data, stepsize=1e-7, glob=1): #consecutive split
    if glob==1:
        rs=np.split(np.argsort(data), np.where(np.diff(sorted(data)) > stepsize)[0]+1)
    elif glob==0:
        rs=np.split(list(range(len(data))), np.where(np.diff(data) > stepsize)[0]+1)
    return rs

ql=Spectrum.objects.all()
Xa=scal([i.y().tolist() for i in ql])
# Xs=savgol(Xa,31,2)
# vr=np.var(Xs,axis=1)
ids=[i.nir_profile_id for i in ql.all()]
profile={'ids':ids,'titles':[NirProfile.objects.get(id=i).title for i in set(ids) if i]}

def obtain_pca(Xa):
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
    # norm=[];_=[norm.extend(min_max_scal(Xa[np.argwhere(gp==i)].squeeze()).tolist()) for i in range(K)]
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
        'spectra':{'ids': [[i.id for i in ql.all()]],'titles':[i.origin for i in ql.all()]},
        'profile':profile,
        'count':ql.count(),
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

def obtain_pca_noScal(Xa):
    # split based on mean and std using KMean:
    #https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
    # mn, st=Xa.mean(axis=1), Xa.std(axis=1)

    # # find the group size (K):
    # sr=np.diff(sorted((mn**2+(st*3)**2)**.5))
    # df=np.diff(np.argwhere(sr>.1).astype(int),axis=0)
    # t,c=[],[]
    # for i in range(len(df)):
    #     if df[i]<5:
    #         c.append(df[i])
    #     else:
    #         if c:
    #             t.append(sum(c))
    #             c=[]
    #         else:
    #             t.append(df[i])
    # if c:
    #     t.append(sum(c))
    # K=len(t)

    # # apply Kmean:
    # kmeans = KMeans(n_clusters=K, random_state=0).fit(np.c_[mn,st*3])
    # gp=kmeans.labels_
    # kmeans.predict(V)
    # plt.scatter(mn,st,c=gp,cmap='viridis');plt.colorbar();plt.show()

    #normlization each group:
    # norm=[];_=[norm.extend(min_max_scal(Xa[np.argwhere(gp==i)].squeeze()).tolist()) for i in range(K)]
    # ixa=[np.argwhere(gp==i).squeeze().tolist() for i in range(K)]
    # stat=[{ 'max': Xa[ixa[i]].max(),
    #         'min': Xa[ixa[i]].min(),
    #         'mean':Xa[ixa[i]].mean(),
    #         'std': Xa[ixa[i]].std(),
    #         'maxs':Xa[ixa[i]].max(axis=1).tolist(),
    #         'mins':Xa[ixa[i]].min(axis=1).tolist()} for i in range(K)]

    # norm=[];_=[norm.extend(((Xa[np.argwhere(gp==i)].squeeze()-stat[i]['mean'])/stat[i]['std']).tolist()) for i in range(K)]

    # ix=[];_=[ix.extend(np.argwhere(gp==i).tolist()) for i in range(K)]
    # ix=[i[0] for i in ix]
    # Xn=np.array(norm)[np.argsort(ix)].squeeze()


    # Apply PCA:
    pca=PCA(n_components=30)
    pca.fit(Xa)
    trans=pca.transform(Xa)
    # km_di=kmeans.__dict__
    # kmean_s={i:(km_di[i].tolist() if type(km_di[i]) is np.ndarray else km_di[i]) for i in km_di}

    pc_di=pca.__dict__
    pca_s={i:(pc_di[i].tolist() if type(pc_di[i]) is np.ndarray else pc_di[i]) for i in pc_di}

    output={
        'title':'PCA spectra',
        'spectra':{'ids': [[i.id for i in ql.all()]],'titles':[i.origin for i in ql.all()]},
        'profile':profile,
        'count':ql.count(),
        'score':pca.score(Xa),
        'n_comp':pca.n_components,
        'trans':trans.tolist(),
        'preprocessed':{
        },
        'applied_model':{'pca':pca_s},

    }
    return output

kwargs=obtain_pca_noScal(Xa)
sm=StaticModel(**kwargs)
sm.save()

# sm=StaticModel.objects.first()
# sm.update(titles=kwargs['titles'],profile=kwargs['profile'])

# lda.fit(Xa,np.c_[mn,st*3].sum(axis=1))
# # split spectrum to 4 groups [very low absorbance, low, high, very high]
# cs=cnsp(vr)
# mcs=[];_=[mcs.extend(i.tolist()) for i in cs[2:4]]
# lcs=[];_=[lcs.extend(i.tolist()) for i in cs[4:]]
# cs=[cs[0].tolist(),cs[1].tolist(),mcs,lcs]
# svagol_stat={'savgol':[{'max':Xs[i].max(),'min':Xs[i].min(),'mean':Xs[i].mean(),'std':Xs[i].std(), 'maxs':Xs[i].max(axis=1).tolist(),'mins':Xs[i].min(axis=1).tolist()} for i in cs]}

# #normlization
# norm=[];_=[norm.extend(min_max_scal(Xs[i]).tolist()) for i in cs]
# ix=[];_=[ix.extend(i) for i in cs]
# Xn=np.array(norm)[np.argsort(ix)]

# # split to training and vildation:
# X,xl,V,org,sl=[],[],[],[],[]
# for a,b in enumerate(ql.all()):
#     org.append(b.origin)
#     if 'rix' in b.origin: # with Brix values
#         X.append(Xn[a].tolist())
#         xl.append(float(re.findall('[\d+\.]+',org[-1])[0]))
#         sl.append(org[-1].split()[0].lower())
#     else:
#         V.append(Xn[a].tolist())

# X=np.array(X)
# V=np.array(V)

# origin = list(set(sl))
# # count = [len([1 for i in q.all() if i.origin.split()[0].lower()==a]) for a in source]
# count = X.shape[0]

# # apply pls:
# pls2 = PLSRegression(n_components=15)
# pls2.fit(X, xl)
# sc=pls2.score(X,xl)

# spec_meta={
#     'count':ql.count(),
#     'preprocessed': svagol_stat,
#     'titles':org
# }
# training_meta={
#     'origin': origin,
#     'count': count,
#     'true_ingre':xl,
#     'pred_ingre':pls2.predict(X).tolist(),
# }
# pls_meta={
#     'v_count': V.shape[0],
#     'v_score': pls2.predict(V).tolist(),
#     'n_components': pls2.n_components,
#     'score': sc,
#     'x_rotations' : pls2.x_rotations_.tolist(),
#     'x_mean' : pls2.x_mean_.tolist(),
#     'y_mean' : pls2.y_mean_.tolist(),
#     'coef' : pls2.coef_.tolist(),
#     'x_std' : pls2.x_std_.tolist(),
#     'trans': pls2.transform(Xn),
# }

