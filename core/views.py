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
from itertools import chain
import numpy as np
from django.core.paginator import Paginator


# def index(request):
#     return HttpResponse("Hello, world. You're at the core index.")


def index(request):
    template = loader.get_template('admin/index_pub.html')
    flat_page=FlatPage.objects.get(url='/welcome/')
    context = {
        'has_permission': request.user.is_authenticated,
        'page': 'welcome',
        'title': flat_page.title,
        'index_text': flat_page.content,
        'figure_header': "Example of interactive plotting:",
        'model':'Spectrum',
        'ids': '4,15,27,38,49'
    }
    
    return HttpResponse(template.render(context, request))

def error_404(request, exception):
        data = {}
        return render(request,'admin/404.html', data)

@csrf_exempt
def upload_auto(request):
    s = Spectrum()
    # for ISC SDK
    file_name = request.POST.get('file_name', '')
    x_received = request.POST.get('x_data', '')
    y_received = request.POST.get('y_data','')
    if file_name and x_received and y_received:
        s.origin = file_name.split('.')[0]
        x_received = x_received[1:-1].split(',')
        s.x_range_min = x_received[0]
        s.x_range_max = x_received[len(x_received) - 1]
        s.y_axis = str(y_received)[1:-1]
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
        # print(model,ids)
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
    #     context.update({})
    #     return context
        
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"})
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
        if model == "NirProfile":  #nir_profile=np.objects.get(id=4))
            nirprofiles=NirProfile.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
            context.update({'max': nirprofiles[0].y_max,})
            spectra=Spectrum.objects.filter(nir_profile= nirprofiles[0])
            for obj in nirprofiles[1:]:
                spectra |=Spectrum.objects.filter(nir_profile= obj)

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

        # print("spectra:",spectra)
        context.update({'model':model,'Spectra': spectra, 'mode': mode})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        if self.cont['mode'] == 'detail':
            x=self.cont['Spectra'].x()
        else:
            x=self.cont['Spectra'].first().x()
        # x= [sorted(list(set(int(round(x[i]/10)*10)))) for i in range(0,len(x),10)]
        x=np.unique((np.round(x/50)*50).astype(int))
        self.cont['x_length']=len(x)
        return x.tolist()

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
        # self.limits={'max','min'}
        x_length=self.cont['x_length']
        # yn=[y[int(a)] for a in np.linspace(0,len(y)-1,x_length)] 
        if self.cont['mode'] == 'detail':
            y=self.cont['Spectra'].y_all()[0]
            # return [i.tolist()[0:-1:10] for i in self.cont['Spectra'].y_all()]
            return [[i.tolist()[a] for a in np.linspace(0,len(i.tolist())-1,x_length).astype(int)] for i in self.cont['Spectra'].y_all()]
        else:
            y=self.cont['Spectra'][0].y()
            return [[i.y().tolist()[a] for a in np.linspace(0,len(i.y().tolist())-1,x_length).astype(int)] for i in self.cont['Spectra']]

# def MpageChecker(request):
#     qset=item.objects.all()
#     paginator=Paginator(qset,30)


# line_chart = TemplateView.as_view(template_name='admin/index1.html')
# line_chart_json = LineChartJSONView.as_view()