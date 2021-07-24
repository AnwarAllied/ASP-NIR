from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# from django_matplotlib import MatplotlibFigureField as ma
from django.contrib.flatpages.models import FlatPage
# import matplotlib.pyplot as plt
from django.core import serializers
from django.db.models import Q
# from django.utils.html import html_safe, mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import Spectrum, NirProfile
from spectraModelling.models import Poly, Match
from preprocessingFilters.models import SgFilter
from django.utils import timezone
import os, re
from django.conf import settings
from django.http import HttpResponse, Http404
from itertools import chain
import numpy as np
import pandas as pd


# def index(request):
#     return HttpResponse("Hello, world. You're at the core index.")


def index(request):
    template = loader.get_template('admin/index_pub.html')
    flat_page=FlatPage.objects.get(url= '/welcome/')
    context = {
        'has_permission': request.user.is_authenticated,
        'page': 'welcome',
        'title': flat_page.title,
        'index_text' : flat_page.content,
        'figure_header': "Example of interactive plotting:",
        'model':'Spectrum',
        'ids': '4,15,27,38,49'
    }
    
    return HttpResponse(template.render(context, request))

def error_404(request, exception):
        data = {}
        return render(request,'admin/404.html', data)

def download_xlsx(request):
    now = timezone.now().__str__()[8:19]
    ids=list(map(int,request.GET.get('ids','').split(',')))
    obj=SgFilter.objects.get(id=ids[0])
    title=obj.nirprofile.first().title
    path=settings.STATICFILES_DIRS[0].__str__()+'/temp/'+title+'-'+now+'.xlsx'
    writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
    # print(ids,path)

    # save the file
    for i in ids:
        # print(i)
        obj=SgFilter.objects.get(id=i)
        title=" ".join(obj.nirprofile.first().title.split()[:3])[:12]
        x_axis=obj.nirprofile.first().spectrum_set.first().x()
        label=[re.findall('\d[\d\.]*',i.origin)[0] if re.findall('\d',i.origin) else '' for i in obj.nirprofile.first().spectrum_set.all()]
        # print(x_axis[:3],x_axis.shape)
        df1 = pd.DataFrame(obj.y())
        # print(obj.y().shape)
        df1.columns=x_axis
        df1.index=label
        df1.to_excel(writer, sheet_name = title)
    
    writer.save()
    writer.close()

    # prepare the download
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
        os.remove(path)  # not trigered, need Signal.
    raise Http404

@csrf_exempt
def upload_auto(request):
    s = Spectrum()
    # for ISC SDK
    file_name = request.POST.get('file_name', '')
    x_received = request.POST.get('x_data', '')
    y_received = request.POST.get('y_data','')
    n_device = request.POST.get('n_device','')
    if file_name and x_received and y_received and n_device:
        s.origin = file_name.split('.')[0]
        x_received = x_received[1:-1].split(',')
        s.x_range_min = x_received[0]
        s.x_range_max = x_received[len(x_received) - 1]
        s.y_axis = str(y_received)[1:-1]
        s.code = n_device
    s.save()
    msg = "Data successfully received by Nirvascan"
    return HttpResponse(msg)

class plot(TemplateView):
    template_name = "admin/index_plot.html"

    def get_context_data(self, **kwargs):
        model=self.request.GET.get('model','')
        ids=self.request.GET.get('ids','')
        # ids=list(map(int,self.request.GET.get('ids','').split(',')))
        data = super().get_context_data()
        # print(dir(self.request.user))
        data["model"]=model
        data["ids"]=ids
        if model == 'Spectrum':
            data["figure_header"]= "Spectra of {}:".format(Spectrum.objects.get(id=int(ids.split(',')[0])).origin.split(' ')[0])
        elif model == 'NirProfile':
            data["figure_header"]= "Spectra of {}:".format(NirProfile.objects.get(id=int(ids.split(',')[0])).title)
        elif model == 'Poly':
            data["figure_header"]= "Poly-modeled spectra of {}:".format(Poly.objects.get(pk=int(ids.split(',')[0])).spectrum.origin.split(' ')[0])
        elif model == 'Match':
            data["figure_header"]= "Uploaded unknown spectra:"

        data["has_permission"]= self.request.user.is_authenticated
        data["app_label"]= 'spectraModelling' if (model == 'Poly' or model == 'Match') else 'core'
        data["verbose_name"]=model
        data["verbose_name_plural"]="figure"
       
        return data
    
   

class LineChartJSONView(BaseLineChartView):
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context.updat({})
    #     return context
        
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"})
        # default_opt.update({'pointRadius': 0})
        return default_opt


    def spect2context(self, **kwargs):
        print('plot url:',self.request.get_full_path())
        # self.dic ={"view": "<core.views.LineChartJSONView object at 0x000002F8626AE940>", "labels": ["January", "February", "March", "April", "May", "June", "July"], "datasets": [{"data": [75, 44, 92, 11, 44, 95, 35], "backgroundColor": "rgba(202, 201, 197, 0.5)", "borderColor": "rgba(202, 201, 197, 1)", "pointBackgroundColor": "rgba(202, 201, 197, 1)", "pointBorderColor": "#fff", "label": "Central", "name": "Central"}, {"data": [41, 92, 18, 3, 73, 87, 92], "backgroundColor": "rgba(171, 9, 0, 0.5)", "borderColor": "rgba(171, 9, 0, 1)", "pointBackgroundColor": "rgba(171, 9, 0, 1)", "pointBorderColor": "#fff", "label": "Eastside", "name": "Eastside"}, {"data": [87, 21, 94, 3, 90, 13, 65], "backgroundColor": "rgba(166, 78, 46, 0.5)", "borderColor": "rgba(166, 78, 46, 1)", "pointBackgroundColor": "rgba(166, 78, 46, 1)", "pointBorderColor": "#fff", "label": "Westside", "name": "Westside"}]}
        # dic = self.dic
        model=self.request.GET.get('model','')
        mode=self.request.GET.get('mode','')
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        # print('spct2con:',model,ids)
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        if model == "NirProfile" or model == 'SgFilter':  #nir_profile=np.objects.get(id=4))
            if model == 'SgFilter':
                SG=SgFilter.objects.get(id= ids[0])
                nirprofiles = SG.nirprofile.all()
                context.update({'SG_y': SG.y(),})
            else:
                nirprofiles=NirProfile.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            context.update({'max': nirprofiles[0].y_max,})
            spectra=Spectrum.objects.filter(nir_profile= nirprofiles[0])
            for obj in nirprofiles[1:]:
                spectra |=Spectrum.objects.filter(nir_profile= obj)
            # Restrict plotting to 100 spectra:
            if spectra.count()>100:
                # print('spectra count:',spectra.count())
                selected = spectra.values_list('pk', flat=True)[:100]
                spectra=spectra.filter(id__in=selected)
                # print('reduced count:',spectra.count())
        elif model == 'Spectrum':
            spectra=Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
        elif model == 'Poly':
            if mode == 'detail':
                spectra=Poly.objects.get(pk=ids[0])
            else:
                spectra=Poly.objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in ids)))
            # print('Model:',spectra[0])
        elif model == 'Match':
            # print('ids:',ids)
            if mode == 'detail':
                match=Match.objects.get(id=ids[0]) # if ',' not in ids else ids.split(',')[0]
            else:
                match=Match.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            spectra=match   # need better overall strcture
            # print('Model:',match)
        # elif model == 'SgFilter':
        #     spectra = SgFilter.objects.get(id= ids[0])
        # print("spectra:",spectra)
        context.update({'model':model ,'Spectra': spectra, 'mode': mode})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        if self.cont['mode'] == 'detail':
            x=self.cont['Spectra'].x()
        # elif self.cont['model']== 'SgFilter':
        #     self.cont['x_length']=self.cont['Spectra'].y().shape[0]
        #     return self.cont['Spectra'].nirprofile.first().title

        else:
            x=self.cont['Spectra'].first().x()
        # x= [sorted(list(set(int(round(x[i]/10)*10)))) for i in range(0,len(x),10)]
        self.request.session['plot_x_h']=x[np.linspace(0,len(x)-1,228).astype(int)].astype(int).tolist()
        x=np.unique((np.round(x/50)*50).astype(int))
        self.cont['x_length']=len(x)
        self.request.session['plot_x_l']=x.tolist()
        return x.tolist()

    def get_providers(self):
        if self.cont['mode'] == 'detail':
            if self.cont['model'] == 'Match':
                label = [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].poly.all()]
            else:
                lable = [self.cont['Spectra'].label()] + [i.label() for i in self.cont['Spectra'].similar_pk.all()]
        else:
        # st='i.spectrum.origin' if self.cont['model'] =="Poly" else 'i.origin'
            label =[i.label() for i in self.cont['Spectra']]
        self.request.session['plot_label_h']=label
        return label
        # return [eval(st) if isinstance(eval(st), str) else eval(st+'()') for i in self.cont['Spectra']]

    def get_data(self):
        # self.limits={'max','min'}
        x_length=self.cont['x_length']
        if self.cont['mode'] == 'detail':
            # y=self.cont['Spectra'].y_all()[0]
            y= np.array([i.tolist() for i in self.cont['Spectra'].y_all()])
            ys= [[i.tolist()[a] for a in np.linspace(0,len(i.tolist())-1,x_length).astype(int)] for i in self.cont['Spectra'].y_all()]
        elif self.cont['model']== 'SgFilter':
            y= self.cont['SG_y']
            ys=y[:,np.linspace(0,y.shape[1]-1,x_length).astype(int)].tolist()

        else:
            # y=self.cont['Spectra'][0].y()
            # y= np.array([i.y().tolist() for i in self.cont['Spectra']])
            y=np.array([[i.y().tolist()[a] for a in np.linspace(0,len(i.y().tolist())-1,228).astype(int)] for i in self.cont['Spectra']])
            ys=[[i.y().tolist()[a] for a in np.linspace(0,len(i.y().tolist())-1,x_length).astype(int)] for i in self.cont['Spectra']]
        self.request.session['plot_y_h']=y.tolist()
        self.request.session['plot_y_l']=ys
        return ys

class LineChartResl(BaseLineChartView):
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"})
        return default_opt

    def get_resl(self):
        resl= self.request.GET.get('resl', '').lower()
        self.resl = resl
        return resl

    def get_labels(self):
        resl= self.get_resl()
        return self.request.session['plot_x_'+resl]

    def get_providers(self):
        return self.request.session['plot_label_h']

    def get_data(self):
        return self.request.session['plot_y_'+self.resl]


# line_chart = TemplateView.as_view(template_name='admin/index1.html')
# line_chart_json = LineChartJSONView.as_view()