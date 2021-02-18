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
from .models import PcaModel, PlsModel
from core.models import Spectrum, NirProfile
from spectraModelling.models import Poly, Match
import json
from itertools import chain
import numpy as np


class pls(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        model = self.request.GET.get('model', '')
        ids = self.request.GET.get('ids','')
        data = super().get_context_data()
        data['model'] = model
        data['ids'] = ids
        if model == 'Spectrum':
            data['figure_header'] = 'PLS model for {}:'.format(Spectrum.objects.get(id=int(ids.split(',')[0])).origin.split(' ')[0])
        elif model == 'NirProfile':
            data['figure_header'] = 'PLS model for {}:'.format(NirProfile.objects.get(id=int(ids.split(',')[0])).title)
        elif model == 'Ploy':
            data['figure_header'] = 'PLS model for {}:'.format(Poly.objects.get(pk=int(ids.split(',')[0])).spectrum.origin.split(' ')[0])
        elif model == 'Match':
            data['figure_header'] = 'Uploaded unknown spectra:'

        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = 'spectraModelling' if (model == 'Poly' or model == 'Match') else 'core'
        data['verbose_name'] = model
        data['verbose_name_plural'] = 'figure'
        data['pls_modeling'] = True
        return data


def pls_save(request):
    if "pls_ids" in request.session.keys():
        pls = PlsModel()
        pls.obtain(request.session['pls_ids'],
                   request.session['trans'],
                   request.session['pls_score'],
                   request.session['pls_mse'],
                   request.session['pls_x_rots'],
                   request.session['pls_y_mean'],
                   request.session['pls_coef'])

        content = {"saved": True, "message": "The model saved successfully, as: " + pls.__str__(), "message_class": "success"}
        # print("x-mean:%s, y-mean:%s,x-std:%s" % (pls.x_mean, pls.y_mean, pls.x_std))
        _=[request.session.pop(i, None) for i in ['pls_ids', 'trans', 'pls_score', 'pls_mse', 'pls_x_rots', 'pls_y_mean', 'pls_coef']]
    else:
        content = {"message": "Sorry, unable to save the model", "message_class": "warning"}
    return HttpResponse(json.dumps(content), content_type="application/json")


class pls_test(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        for i in ['model', 'ids', 'model_id']:
            data[i] = self.request.GET.get(i, '')

        data["has_permission"] = self.request.user.is_authenticated
        data["app_label"] = 'predictionModel'
        data["verbose_name"] = 'PlsModel'
        data["verbose_name_plural"] = "figure"
        data['pls_modeling'] = True
        data["plot_mode"] = True
        data['title'] = 'Testing set for the model:'
        data['index_text'] = PlsModel.objects.get(id=data['model_id']).__str__()

        return data


class PlsScatterChartView(BaseLineChartView):
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"})
        default_opt.update({'pointRadius': 5})
        return default_opt

    def spect2context(self, **kwargs):
        model = self.request.GET.get('model', '')
        mode = self.request.GET.get('mode', '')
        model_id=self.request.GET.get('model_id','')
        model_id= int(model_id) if model_id else model_id
        ids = list(map(int, self.request.GET.get('ids', '').split(',')))
        self.request.session['model'] = model
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        if model == "NirProfile":
            nirprofiles = NirProfile.objects.filter(eval('|'.join('Q(id=' + str(pk) + ')' for pk in ids)))
            context.update({'max': nirprofiles[0].y_max, })
            spectra = Spectrum.objects.filter(nir_profile=nirprofiles[0])
            for obj in nirprofiles[1:]:
                spectra |= Spectrum.objects.filter(nir_profile=obj)
            ids = [i.id for i in spectra]
        elif model == 'Spectrum':
            spectra = Spectrum.objects.filter(eval('|'.join('Q(id=' + str(pk) + ')' for pk in ids)))

        elif model == 'PlsModel':
            if mode == 'detail':
                pls = PlsModel.objects.get(pk=ids[0])
                spectra = pls.calibration
                # print([i.id for i in spectra.all()])
            elif model_id:
                pls = PlsModel.objects.get(id=model_id)
                spectra = Spectrum.objects.filter(eval('|'.join('Q(pk=' + str(pk) + ')' for pk in ids)))
            else:
                pls = PlsModel.objects.filter(eval('|'.join('Q(pk=' + str(pk) + ')' for pk in ids)))
                spectra = pls.calibration
            # print('Model:',spectra.all()[0])
        elif model == 'Match':
            if mode == 'detail':
                match = Match.objects.get(id=ids[0])  # if ',' not in ids else ids.split(',')[0]
            else:
                match = Match.objects.filter(eval('|'.join('Q(id=' + str(pk) + ')' for pk in ids)))
            spectra = match

        # PLS:
        if 'pls' in locals():
            if model_id:
                trans, score, mse, x_rotations, y_mean, coef = pls.apply('test', *ids)
            else:
                trans, score, mse, x_rotations, y_mean, coef = pls.trans(), pls.score, pls.mse, pls.xrots(), pls.ymean(), pls.pcoef()
                # print('xrots:%s, xmean:%s' % (x_rotations,x_mean))
        else:
            pls = PlsModel()
            trans, score, mse, x_rotations, y_mean, coef = pls.apply('calibration', *ids)
        # keep a copy at session in case saving it:
        self.request.session['trans'] = trans.tolist()
        self.request.session['pls_ids'] = ids
        self.request.session['pls_score'] = score
        self.request.session['pls_mse'] = mse
        self.request.session['pls_x_rots'] = x_rotations.tolist()
        self.request.session['pls_y_mean'] = y_mean.tolist()
        self.request.session['pls_coef'] = coef.tolist()
        # print("spectra:",spectra)
        context.update({'model': model, 'Spectra': spectra, 'trans': trans, 'mode': mode})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        return self.get_providers()

    def get_providers(self):
        if self.cont['mode'] == 'detail':
            if self.cont['model'] == 'PlsModel':
                return [i.origin for i in self.cont['Spectra'].all()]
            else:
                return [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].similar_pk.all()]
        else:
            return [i.label() for i in self.cont['Spectra']]

    def get_data(self):
        trans=self.cont['trans']
        # l=len(trans.T)
        # if l<2:
        #     trans=np.array([list(range(len(trans[0]))),trans[0].tolist()])
        return [[{"x":a,"y":b}] for a,b in trans[:,:2]]#[{"x":1,"y":2},{"x":5,"y":4}],[{"x":3,"y":4},{"x":3,"y":1}]]#


class pca(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        model=self.request.GET.get('model','')
        ids=self.request.GET.get('ids','')
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
    if "comp" in request.session.keys(): # check if a session copy available
        pca=PcaModel()
        pca.obtain(request.session['comp'], request.session['pca_ids'], request.session['trans'], request.session['pca_score'])
        print("model:", pca.__str__(),"saved")
        content = {"saved":True,"message":"The model saved successfully, as: " + pca.__str__(),"message_class" : "success" }
        # resest session:
        _=[request.session.pop(i, None) for i in ['comp', 'pca_ids', 'trans','pca_score']]
    else:
        content = {"message":"Sorry! unable to save the model","message_class" : "warning" }
    return HttpResponse(json.dumps(content),  content_type = "application/json")
    
class pca_test(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        for i in ['model','ids','model_id']:
            data[i]=self.request.GET.get(i,'')
            
        data["has_permission"]= self.request.user.is_authenticated
        data["app_label"]= 'predictionModel'
        data["verbose_name"]='PcaModel'
        data["verbose_name_plural"]="figure"
        data['scartter']=True
        data["plot_mode"]=True

        data['title']='Testing set for the model:'
        data['index_text']= PcaModel.objects.get(id=data['model_id']).__str__()

        return data

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
        model_id=self.request.GET.get('model_id','')
        model_id= int(model_id) if model_id else model_id
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        self.request.session['model']=model
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        if model == "NirProfile":
            nirprofiles=NirProfile.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            context.update({'max': nirprofiles[0].y_max,})
            spectra=Spectrum.objects.filter(nir_profile= nirprofiles[0])
            for obj in nirprofiles[1:]:
                spectra |=Spectrum.objects.filter(nir_profile= obj)
            ids=[i.id for i in spectra]
        elif model == 'Spectrum':
            spectra=Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            
        elif model == 'PcaModel':
            if mode == 'detail':
                pca=PcaModel.objects.get(pk=ids[0])
                spectra = pca.calibration
            elif model_id:
                pca=PcaModel.objects.get(id=model_id)
                spectra = Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            else:
                pca=PcaModel.objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in ids)))
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
        if "pca" in locals():
            if model_id:
                comp, trans, score=pca.apply('test',*ids)
            else:
                comp, trans, score=pca.comp(), pca.trans(), pca.score
        else:
            pca=PcaModel()
            comp, trans, score=pca.apply('calibration',*ids)
        # keep a copy at session in case saving it:
        self.request.session['comp']=comp.tolist()
        self.request.session['trans']=trans.tolist()
        self.request.session['pca_ids']=ids
        self.request.session['pca_score']=score
        # print("spectra:",spectra)
        context.update({'model':model ,'Spectra': spectra, 'trans': trans, 'mode': mode})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        return self.get_providers()

    def get_providers(self):
        if self.cont['mode'] == 'detail':
            if self.cont['model'] == 'PcaModel':
                return [i.origin for i in self.cont['Spectra'].all()]
            else:
                return [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].similar_pk.all()]
        else:
            return [i.label() for i in self.cont['Spectra']]

    def get_data(self):
        trans=self.cont['trans']
        # l=len(trans.T)
        # if l<2:
        #     trans=np.array([list(range(len(trans[0]))),trans[0].tolist()])
        return [[{"x":a,"y":b}] for a,b in trans[:,:2]]#[{"x":1,"y":2},{"x":5,"y":4}],[{"x":3,"y":4},{"x":3,"y":1}]]#
