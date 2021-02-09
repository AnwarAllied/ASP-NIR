from django.shortcuts import render
from django.http import HttpResponse
# from django.template import loader
# from django_matplotlib import MatplotlibFigureField as ma
# from django.contrib.flatpages.models import FlatPage
# import matplotlib.pyplot as plt
from django.core import serializers
from django.db.models import Q
# from django.utils.html import html_safe, mark_safe
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import PcaModel
from core.models import Spectrum, NirProfile
from spectraModelling.models import Poly, Match
import json
from itertools import chain
import numpy as np

class pls(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        model = self.request.GET.get('model', '')
        ids = self.request.GET.get('ids', '')
        data = super().get_context_data()
        data['model'] = model
        data['ids'] = ids
        if model == 'Spectrum':
            data['figure_header'] = 'PLS model for {}:'.format(Spectrum.object.get(id=int(ids.split(',')[0])).origin.split(' ')[0])
        elif model == 'NirProfile':
            data['figure_header'] = 'PLS model for {}:'.format(NirProfile.object.get(id=int(ids.split(',')[0])).title)
        elif model == 'Ploy':
            data['figure_header'] = 'PLS model for {}:'.format(Poly.object.get(pk=int(ids.split(',')[0])).spectrum.origin.split(' ')[0])
        elif model == 'Match':
            data['figure_header'] = 'Uploaded unknown spectra:'

        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = 'spectraModelling' if (model == 'Poly' or model == 'Match') else 'core'
        data['verbose_name'] = model
        data['verbose_name_plural'] = 'figure'

        return data

# Create your views here.
class pca(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        model=self.request.GET.get('model','')
        ids=self.request.GET.get('ids','')
        # ids=list(map(int,self.request.GET.get('ids','').split(',')))
        data = super().get_context_data()
        # print(dir(self.request.user))
        data["model"]=model
        data["ids"]=ids
        print('PCA',model,ids)
        if model == 'Spectrum':
            data["figure_header"]= "PCA model for {}:".format(Spectrum.objects.get(id=int(ids.split(',')[0])).origin.split(' ')[0])
        elif model == 'NirProfile':
            data["figure_header"]= "PCA model for {}:".format(NirProfile.objects.get(id=int(ids.split(',')[0])).title)
        elif model == 'Poly':
            data["figure_header"]= "PCA model for {}:".format(Poly.objects.get(pk=int(ids.split(',')[0])).spectrum.origin.split(' ')[0])
        elif model == 'Match':
            data["figure_header"]= "Uploaded unknown spectra:"

        data["has_permission"]= self.request.user.is_authenticated
        data["app_label"]= 'spectraModelling' if (model == 'Poly' or model == 'Match') else 'core'
        data["verbose_name"]=model
        data["verbose_name_plural"]="figure"
        data['scartter']=True
       
        return data

def pca_save(request):
    print('saving the PCA model')
    if "components" in request.session.keys(): # check if a session copy availible
        pca=PcaModel()
        pca.obtain(request.session['components'], request.session['pca_ids'], request.session['pca_score'])
        print("model:", pca.__str__(),"saved")
        content = {"saved":True,"message":"The model saved successfully, as: " + pca.__str__(),"message_class" : "success" }
    else:
        content = {"message":"Sorry! unable to save the model","message_class" : "warning" }
    return HttpResponse(json.dumps(content) ,  content_type = "application/json")
    
   

class ScartterChartView(BaseLineChartView):
        
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"}) # disable the area filling in ChartJS options
        default_opt.update({'pointRadius': 5})
        return default_opt


    def spect2context(self, **kwargs):
        print('Scartter url:',self.request.get_full_path())
        model=self.request.GET.get('model','')
        mode=self.request.GET.get('mode','')
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        self.request.session['model']=model
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        if model == "NirProfile":  #nir_profile=np.objects.get(id=4))
            nirprofiles=NirProfile.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            context.update({'max': nirprofiles[0].y_max,})
            spectra=Spectrum.objects.filter(nir_profile= nirprofiles[0])
            for obj in nirprofiles[1:]:
                spectra |=Spectrum.objects.filter(nir_profile= obj)
            ids=[i.id for i in spectra]
        elif model == 'Spectrum':
            spectra=Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            
        elif model == 'Poly':
            if mode == 'detail':
                spectra=Poly.objects.get(pk=ids[0])
            else:
                spectra=Poly.objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in ids)))
            # print('Model:',spectra[0])
        elif model == 'Match':
            print('ids:',ids)
            if mode == 'detail':
                match=Match.objects.get(id=ids[0]) # if ',' not in ids else ids.split(',')[0]
            else:
                match=Match.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            spectra=match   # need better overall strcture
            # print('Model:',match)
        # PCA:
        pca=PcaModel()
        components, score=pca.apply('calibration',*ids)
        # keep a copy at session in case saving it:
        self.request.session['components']=components.tolist()
        self.request.session['pca_ids']=ids
        self.request.session['pca_score']=score
        # print("spectra:",spectra)
        context.update({'model':model ,'Spectra': spectra, 'components': components.T, 'mode': mode})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        return self.get_providers()

    def get_providers(self):
        if self.cont['mode'] == 'detail':
            if self.cont['model'] == 'Match':
                return [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].poly.all()]
            else:
                return [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].similar_pk.all()]
        else:
            return [i.label() for i in self.cont['Spectra']]

    def get_data(self):
        C=self.cont['components']
        l=len(C)
        if l<2:
            C=np.array([list(range(len(C[0]))),C[0].tolist()])
        
        return [[{"x":a,"y":b}] for a,b in C[:2].T]#[{"x":1,"y":2},{"x":5,"y":4}],[{"x":3,"y":4},{"x":3,"y":1}]]#
