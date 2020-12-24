from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django_matplotlib import MatplotlibFigureField as ma
# import matplotlib.pyplot as plt
from django.core import serializers
from django.db.models import Q

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import Spectrum, NirProfile

# def index(request):
#     return HttpResponse("Hello, world. You're at the core index.")

def index(request):
    template = loader.get_template('admin/index1.html')
    context = {
        'whelcome': "Hello, world. You're at the core index.",
    }
    return HttpResponse(template.render(context, request))

class plot(TemplateView):
    template_name = "admin/index1.html"

    def get_context_data(self, **kwargs):
        
        model=self.request.GET.get('model','')
        ids=self.request.GET.get('ids','')
        # ids=list(map(int,self.request.GET.get('ids','').split(',')))
        data = super().get_context_data()

        data["model"]=model
        data["ids"]=ids

        return data
    
   

class LineChartJSONView(BaseLineChartView):

    def spect2context(self, **kwargs):
        self.dic ={"view": "<core.views.LineChartJSONView object at 0x000002F8626AE940>", "labels": ["January", "February", "March", "April", "May", "June", "July"], "datasets": [{"data": [75, 44, 92, 11, 44, 95, 35], "backgroundColor": "rgba(202, 201, 197, 0.5)", "borderColor": "rgba(202, 201, 197, 1)", "pointBackgroundColor": "rgba(202, 201, 197, 1)", "pointBorderColor": "#fff", "label": "Central", "name": "Central"}, {"data": [41, 92, 18, 3, 73, 87, 92], "backgroundColor": "rgba(171, 9, 0, 0.5)", "borderColor": "rgba(171, 9, 0, 1)", "pointBackgroundColor": "rgba(171, 9, 0, 1)", "pointBorderColor": "#fff", "label": "Eastside", "name": "Eastside"}, {"data": [87, 21, 94, 3, 90, 13, 65], "backgroundColor": "rgba(166, 78, 46, 0.5)", "borderColor": "rgba(166, 78, 46, 1)", "pointBackgroundColor": "rgba(166, 78, 46, 1)", "pointBorderColor": "#fff", "label": "Westside", "name": "Westside"}]}
        dic = self.dic
        model=self.request.GET.get('model','')
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        print('spct2con:',model,ids)
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        context.update({'Spectra': Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))})
        context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spect2context()
        x=list(map(int,self.cont['Spectra'].first().x()))
        return x+[]

    def get_providers(self):
        return [i.origin for i in self.cont['Spectra']]

    def get_data(self):
        return [i.y().tolist() for i in self.cont['Spectra']]




# line_chart = TemplateView.as_view(template_name='admin/index1.html')
# line_chart_json = LineChartJSONView.as_view()