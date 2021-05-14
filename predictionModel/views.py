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
from preprocessingFilters.models import SgFilter
import json
from itertools import chain
import numpy as np
from .mng import get_title_color
from .dataHandeller import datasheet4testing
from django.contrib import messages
from django.http import HttpResponseRedirect

class pls(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        model = self.request.GET.get('model', '')
        ids = self.request.GET.get('ids','')
        components = self.request.GET.get('components','')
        data = super().get_context_data()
        data['model'] = model
        data['ids'] = ids
        if components:
            data['components']=components
        if model == 'Spectrum':
            data['figure_header'] = 'PLS model for {}:'.format(Spectrum.objects.get(id=int(ids.split(',')[0])).origin.split(' ')[0])
        elif model == 'NirProfile':
            data['figure_header'] = 'PLS model for {}:'.format(NirProfile.objects.get(id=int(ids.split(',')[0])).title)
        elif model == 'SgFilter':
            data['figure_header'] = 'PLS model SG filter for {}:'.format(SgFilter.objects.get(id=int(ids.split(',')[0])).nirprofile.first().title)   
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
        if 'preprocessed' not in request.session.keys():
            request.session['preprocessed'] =None
        pls = PlsModel()
        pls.obtain(request.session['pls_ids'],
                   request.session['trans'],
                   request.session['components'],
                   request.session['pls_score'],
                   request.session['pls_mse'],
                   request.session['pls_x_rots'],
                   request.session['pls_x_mean'],
                   request.session['pls_y_mean'],
                   request.session['pls_coef'],
                   request.session['pls_x_std'],
                   request.session['pls_y_pred'],
                   request.session['preprocessed'],
        )

        content = {"saved": True, "message": "The model saved successfully, as: " + pls.__str__(), "message_class": "success"}
        # print("x-mean:%s, y-mean:%s,x-std:%s" % (pls.x_mean, pls.y_mean, pls.x_std))
        _=[request.session.pop(i, None) for i in ['pls_ids', 'trans', 'components', 'pls_score', 'pls_mse', 'pls_x_rots', 'pls_x_mean','pls_y_mean', 'pls_coef','pls_x_std','pls_y_pred','preprocessed']]
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

    def get_context_data(self, **kwargs):
        # context = super(BaseLineChartView, self).get_context_data(**kwargs)
        model_id=self.request.GET.get('model_id','')
        content={"labels": self.get_labels(), "datasets": self.get_datasets()}
        try:
            if model_id:
                unit=Spectrum.objects.get(id=int(model_id)).origin.split()[2]
            else:
                unit=self.cont['Spectra'].first().origin.split()[2]
        except:
            unit=None
        
        context=self.cont
        _=[context.pop(i, None) for i in ['Spectrum', 'y_pred', 'trans','model']]
        context.update(content)
        context.update({"title": True if model_id else False, 'text': 'Validation set Rsquared= '+ ('00.00' if self.cont['score']< 0 else "{:0.4f}".format(self.cont['score'])), 'axis_unit': unit } )
        return context

    def spect2context(self, **kwargs):
        model = self.request.GET.get('model', '')
        mode = self.request.GET.get('mode', '')
        model_id=self.request.GET.get('model_id','')
        model_id= int(model_id) if model_id else model_id
        components = self.request.GET.get('components', '')
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
            query=nirprofiles
        elif model == 'SgFilter':  #nir_profile=np.objects.get(id=
            SG=SgFilter.objects.get(id= ids[0])
            # print(ids,SG)
            nirprofiles = SG.nirprofile.all()
            context.update({'SG_y': SG.y(),'max': nirprofiles[0].y_max})
            spectra = nirprofiles[0].spectrum_set.all()
            # must consider nirprofilres with no Spectra
            for obj in nirprofiles[1:]:
                spectra |= Spectrum.objects.filter(nir_profile=obj)
            ids = [i.id for i in spectra]
            # print('SG ids:',ids)
            query=SG
            self.request.session['preprocessed']= model+','+str(SG.id)
        elif model == 'Spectrum':
            spectra = Spectrum.objects.filter(eval('|'.join('Q(id=' + str(pk) + ')' for pk in ids)))
            query=None
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
                # if pls.preprocessed:
                #     SG=SgFilter.objects.get(id=int(pls.preprocessed.split(',')[1]))
                #     spectra= SG.nirprofile.first().spectrum_set.all()
                #     ids = [i.id for i in spectra]
                #     query=SG
                # else:
                spectra = pls.calibration
            query=None
            # print('Model:',spectra.all()[0])
            
        elif model == 'Match':
            if mode == 'detail':
                match = Match.objects.get(id=ids[0])  # if ',' not in ids else ids.split(',')[0]
            else:
                match = Match.objects.filter(eval('|'.join('Q(id=' + str(pk) + ')' for pk in ids)))
            spectra = match
            query=None

        # PLS:
        if 'pls' in locals():
            if model_id: # if avalible: test or show it
                trans, components, score, mse, x_rotations, x_mean, y_mean, coef, x_std, y_pred, ids_filtred, y_true = pls.apply('test', pls.order, *ids, model=query)
            else:
                trans, components, score, mse, x_rotations, x_mean, y_mean, coef, x_std, y_pred, ids_filtred, y_true = pls.trans(), pls.order, pls.score, pls.mse, pls.xrots(), pls.xmean(), pls.ymean(), pls.pcoef(), pls.xstd(), pls.ypred(), pls.get_calibration_ids(), pls.get_y_train()
                # context.update({'model': model, 'Spectra': spectra, 'trans': trans, 'mode': mode, 'y_pred': y_pred})
                # return context
        else: # if new pls
            pls = PlsModel()
            if components:
                components=int(components)
                pls.order=components
                print('Components setted to:',components)
            else:
                components = 10 if spectra.count()>20 else 2
                
            trans, components, score, mse, x_rotations, x_mean, y_mean, coef, x_std, y_pred, ids_filtred, y_true = pls.apply('calibration', components, *ids, model=query)
            # keep a copy at session in case saving it:
            self.request.session['trans'] = trans.tolist()
            self.request.session['pls_ids'] = ids_filtred
            self.request.session['pls_score'] = score
            self.request.session['components'] = components
            self.request.session['pls_mse'] = mse
            self.request.session['pls_x_rots'] = x_rotations.tolist()
            self.request.session['pls_x_mean'] = x_mean.tolist()
            self.request.session['pls_y_mean'] = y_mean.tolist()
            self.request.session['pls_coef'] = coef.tolist()
            self.request.session['pls_x_std'] = x_std.tolist()
            self.request.session['pls_y_pred'] = y_pred.tolist()
            
        context.update({'model': model, 'Spectra': spectra, 'trans': trans, 'mode': mode, 'y_pred': y_pred, 'score': score, 'ids_filtred':ids_filtred, 'y_true': y_true})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        # self.cont['providers']= self.get_providers()
        # ids_filtred = self.cont['ids_filtred']
        # print("in lebles")
        return []#['jhkhj','jkhk','fjhhjff','gyui','iuyiu']#[Spectrum.objects.get(id= i).origin for i in ids_filtred]

    # def isDigit(self,x):
    #     try:
    #         float(x)
    #         return True
    #     except ValueError:
    #         return False

    def get_providers(self):
        # if 'providers' in self.cont.keys():
        #     return self.cont['providers']
        
        model_id = self.request.GET.get('model_id', '')
        ids_filtred = self.cont['ids_filtred']
        return [Spectrum.objects.get(id= i).origin for i in ids_filtred]
        # if self.cont['mode'] == 'detail':
        #     if self.cont['model'] == 'PlsModel':
        #         return [i.origin for i in self.cont['Spectra'].all()]
        #     else:
        #         return [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].similar_pk.all()]
        # elif model_id:
        #     ids_filtred = self.cont['ids_filtred']
        #     spectra = list(range(len(ids_filtred)))
        #     for i in range(len(ids_filtred)):
        #         spectra[i]=Spectrum.objects.get(id=ids_filtred[i])
        #         spectra_name_items = spectra[i].origin.split()
        #         # modify the origin number of a spectrum
        #         if len(spectra_name_items)>1 and self.isDigit(spectra_name_items[1])==True:
        #             spectra_name_items[1] += ' (predicted: '+'{:0.2f}'.format(self.cont['y_pred'][i][0])+')'
        #             spectra[i].origin = ' '.join(spectra_name_items)
        #         else:
        #             spectrum.origin += ' (predicted: '+'{:0.2f}'.format(self.cont['y_pred'][i][0])+')'
        #     return [Spectrum.objects.get(id= i).origin for i in ids_filtred] #[i.label() for i in spectra]
        # else:
        #     return [i.label() for i in self.cont['Spectra']]

    def get_data(self):
        y_true=self.cont['y_true'].tolist()
        y_pred=self.cont['y_pred'].tolist()
        # trans=self.cont['trans']
        # l=len(trans.T)
        # if l<2:
        #     trans=np.array([list(range(len(trans[0]))),trans[0].tolist()])
        # return [[{"x":a,"y":b}] for a,b in trans[:,:2]]#[{"x":1,"y":2},{"x":5,"y":4}],[{"x":3,"y":4},{"x":3,"y":1}]]#
        return [[{"x":a,"y":b}] for a,b in zip(y_true,y_pred)]#[{"x":1,"y":2},{"x":5,"y":4}],[{"x":3,"y":4},{"x":3,"y":1}]]#


# Create your views here.
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
        data['scartter2']=True
        # data['obj_id']=2
        # data['master_static_pca']=True
        return data

def pca_save(request):
    print('saving the PCA model')
    if "comp" in request.session.keys(): # check if a session copy availible
        pca=PcaModel()
        pca.obtain(request.session['comp'], request.session['pca_ids'], request.session['trans'], request.session['pca_score'])
        print("model:", pca.__str__(),"saved")
        content = {"saved":True,"message":"The model saved successfully, as: " + pca.__str__(),"message_class" : "success" }
        # resest session:
        _=[request.session.pop(i, None) for i in ['comp', 'pca_ids', 'trans','pca_score']]
    else:
        content = {"message":"Sorry! unable to save the model","message_class" : "warning" }
    return HttpResponse(json.dumps(content) ,  content_type = "application/json")
    
class pca_test(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        for i in ['model','ids','model_id','pca_upload']:
            data[i]=self.request.GET.get(i,'')
        
        data["has_permission"]= self.request.user.is_authenticated
        # data['ids']=data['model_id']
        # data["obj_id"]= 2
        data["pca_tag"]='&pca_id='+data['model_id']+'&pca_ids='+data['ids']+'&pca_up='+data['pca_upload']
        data["app_label"]= 'predictionModel'
        data["model"]='PcaModel'
        data["verbose_name"]='PcaModel'
        data["verbose_name_plural"]="figure"
        # data['scartter']=True
        # data["plot_mode"]=True
        data['scartter2'] = True
        data['title']='Testing set for the model:'
        data['index_text']= PcaModel.objects.get(id=data['model_id']).__str__() #not showing
        return data

def pca_upload(request,**kyargs):
    if request.method == 'POST':
        # print(kyargs)
        print('file:',request.FILES.keys())
        Pca = PcaModel.objects.get(id=kyargs['id'])
    if 'upload_a_spectrum_for_testing' in request.FILES.keys():
        dsFile=request.FILES['upload_a_spectrum_for_testing'].file
        dsFile.seek(0)
        y_axis,msg=datasheet4testing(file=dsFile, filename=str(request.FILES['upload_a_spectrum_for_testing']))
        print('name :',str(request.FILES['upload_a_spectrum_for_testing']))
        
        if not y_axis:
            messages.error(request, 'Sorry, the uploaded file is not formated properly.')
            return HttpResponseRedirect("/admin/predictionModel/pcamodel/%s/change/" % kyargs['id'] )

        request.session['pca_upload']= y_axis
        
        return HttpResponseRedirect("/pca/test/?model=PcaModel&model_id=%s&pca_upload=1" % kyargs['id'])
    else:
        messages.error(request, 'Sorry, nothing to upload.')
        return HttpResponseRedirect("/admin/predictionModel/pcamodel/%s/change/" % kyargs['id'] )



class ScartterChartView(BaseLineChartView):
    def get_context_data(self,**kwargs):
        content = {"labels": self.get_labels()}
        datasets=self.get_datasets()
        
        # sort by profile color:
        color_ix={}
        colors, co_titles, colorset=get_title_color(content['labels'])
        for i in range(len(colors)):
            datasets[i]['pointBackgroundColor']=colors[i]
            if colors[i] not in color_ix:
                color_ix.update({datasets[i]['pointBackgroundColor']:i})
        for i in color_ix.values():
            datasets[i]['label']=co_titles[i].capitalize()
        if 'selected_ln' in self.cont:
            ln=self.cont['selected_ln']
            sids=self.cont['selected_ids']
            oids=self.cont['obj_ids']
            sr=np.argsort(oids+sids)
            sr =[i for i in sr if i>(len(datasets)-ln)]
            print(sr,oids+sids)
            for i in sr:#[:ln]: #range(len(datasets))[:ln-2]:
                datasets[i]['pointStyle']='rect'
                datasets[i]['pointRadius']= 5
                datasets[i]['label']=datasets[i]['label']+'-selected test'
            # if self.cont['pca_test']== 1:
            #     datasets[-1]['label']=datasets[-1]['label']+': identified as '+self.cont['msg'][-1] 

        content.update({"datasets": datasets,"color_ix":list(color_ix.values())})
        context=self.cont
        context.update(content)
        return context


        
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
        print(len(ids))
        self.request.session['model']=model
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        if model == "NirProfile":  #nir_profile=np.objects.get(id=4))
            nirprofiles=NirProfile.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            context.update({'max': nirprofiles[0].y_max,})
            spectra=Spectrum.objects.filter(nir_profile= nirprofiles[0])
            for obj in nirprofiles[1:]:
                spectra |=Spectrum.objects.filter(nir_profile= obj)
            spectra=spectra.order_by('id')
            ids=[i.id for i in spectra]
        elif model == 'Spectrum':
            spectra=Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in sorted(ids))))
            ids=[i.id for i in spectra]
        elif model == 'PcaModel':
            if mode == 'detail':
                pca=PcaModel.objects.get(pk=ids[0])
                spectra = pca.calibration.order_by('id')
                ids=[i.id for i in spectra.all()]
            elif model_id:
                # print('_'*80)
                pca=PcaModel.objects.get(id=model_id)
                oids=sorted([i.id for i in pca.calibration.all()])
                spectra = Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in oids+sorted(ids))))
                context.update({'obj_ids':oids,'selected_ln':len(ids),'selected_ids':ids})
                ids=[i.id for i in spectra]
            else:
                pca=PcaModel.objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in sorted(ids))))
                ids=[i.pk for i in pca]
            # print('Model:',spectra[0])
        elif model == 'Match':
            # print('ids:',ids)
            if mode == 'detail':
                match=Match.objects.get(id=ids[0]) # if ',' not in ids else ids.split(',')[0]
            else:
                match=Match.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in sorted(ids))))
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
