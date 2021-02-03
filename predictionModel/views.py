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

from itertools import chain
import numpy as np

class pls(TemplateView):
    pass

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
    
   

class ScartterChartView(BaseLineChartView):
        
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"}) # disable the area filling in ChartJS options
        default_opt.update({'pointRadius': 5})
        return default_opt


    def spect2context(self, **kwargs):
        print('Scartter url:',self.request.get_full_path())
        # self.dic ={"view": "<core.views.LineChartJSONView object at 0x000002F8626AE940>", "labels": ["January", "February", "March", "April", "May", "June", "July"], "datasets": [{"data": [75, 44, 92, 11, 44, 95, 35], "backgroundColor": "rgba(202, 201, 197, 0.5)", "borderColor": "rgba(202, 201, 197, 1)", "pointBackgroundColor": "rgba(202, 201, 197, 1)", "pointBorderColor": "#fff", "label": "Central", "name": "Central"}, {"data": [41, 92, 18, 3, 73, 87, 92], "backgroundColor": "rgba(171, 9, 0, 0.5)", "borderColor": "rgba(171, 9, 0, 1)", "pointBackgroundColor": "rgba(171, 9, 0, 1)", "pointBorderColor": "#fff", "label": "Eastside", "name": "Eastside"}, {"data": [87, 21, 94, 3, 90, 13, 65], "backgroundColor": "rgba(166, 78, 46, 0.5)", "borderColor": "rgba(166, 78, 46, 1)", "pointBackgroundColor": "rgba(166, 78, 46, 1)", "pointBorderColor": "#fff", "label": "Westside", "name": "Westside"}]}
        # dic = self.dic
        model=self.request.GET.get('model','')
        mode=self.request.GET.get('mode','')
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        # print('spct2con:',model,ids)
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
        components=pca.apply('calibration',*ids)
        # print("spectra:",spectra)
        context.update({'model':model ,'Spectra': spectra, 'components': components, 'mode': mode})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        return list(range(len(self.cont['components'][0])))

    def get_providers(self):
        if self.cont['mode'] == 'detail':
            if self.cont['model'] == 'Match':
                return [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].poly.all()]
            else:
                return [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].similar_pk.all()]
        else:
        # st='i.spectrum.origin' if self.cont['model'] =="Poly" else 'i.origin'
            return [i.label() for i in self.cont['Spectra']]
        # return [eval(st) if isinstance(eval(st), str) else eval(st+'()') for i in self.cont['Spectra']]

    def get_data(self):
        C=self.cont['components']
        l=len(C)
        if l<2:
            C=np.array([list(range(len(C[0]))),C[0].tolist()])
        
        return [[{"x":a,"y":b}] for a,b in C[:2].T]#[{"x":1,"y":2},{"x":5,"y":4}],[{"x":3,"y":4},{"x":3,"y":1}]]#


# from predictionModel.models import PcaModel as pca
# p=pca.objects.first()
# p.obtain()