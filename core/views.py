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
        print(kwargs)
        print(type(kwargs))
        
        model=self.request.GET.get('model','')
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        print(model,ids)
        data = super().get_context_data(**kwargs)
        data['Spectra'] = Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
        data['s1']=[i.y().tolist() for i in data['Spectra']]
        return data
    
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        print(self.request.get_full_path())
        """Return 3 datasets to plot."""
        s1=Spectrum.objects.all()[0].y().tolist()
        s2=Spectrum.objects.all()[1].y().tolist()
        s3=s1[:25]+s2[25:]
        return [s1,s2,s3]
    # plt.plot(range(100))
    # fig=plt.gcf()
    # buf=io.BytesIO()
    # fig.savefig(buf,format="png")
    # buf.seek(0)
    # string = base64.b64decode(buf.read())
    # uri = urllib.parse.quote(string)
    # return render(request,'admin/index1.html',{'data':uri})
    # fig=ma(figure='my_figure')
    # # return HttpResponse(str(dir(request))+str(request))
    # response = HttpResponse(content_type="application/json")
    # # print(dir(response),'\n',response.content)
    # serializers.serialize("json", fig, stream=response)
    # print(dir(response),'\n',response.content)
    # return response

class LineChartJSONView(BaseLineChartView):
    
    def get_context_data(self, **kwargs):
        print(kwargs)
        print(type(kwargs))
        
        model=self.request.GET.get('model','')
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        print(model,ids)
        data = super().get_context_data(**kwargs)
        data['Spectra'] = Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
        data['s1']=[i.y().tolist() for i in data['Spectra']]
        

        def self.get_labels(self,data):
            """Return 7 labels for the x-axis."""
            return ["January", "February", "March", "April", "May", "June", "July"]

        def self.get_providers(self):
            """Return names of datasets."""
            return ["Central", "Eastside", "Westside"]

        def self.get_data(self):
            print(self.request.get_full_path())
            """Return 3 datasets to plot."""
            s1=Spectrum.objects.all()[0].y().tolist()
            s2=Spectrum.objects.all()[1].y().tolist()
            s3=s1[:25]+s2[25:]
            return [s1,s2,s3]
            # return [[75, 44, 92, 11, 44, 95, 35],
            #         [41, 92, 18, 3, 73, 87, 92],
            #         [87, 21, 94, 3, 90, 13, 65]]

    def ips2data(self,**kwargs):
        
        model=self.request.GET.get('model','')
        ids=list(map(int,self.request.GET.get('ids','').split(',')))
        print(model,ids)
        data = super().get_context_data(**kwargs)
        data['Spectra'] = Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ids)))
        data['y_axis']=[i.y().tolist() for i in data['Spectra']]
        data['origin']=[i.origin for i in data['Spectra']]
        return data



line_chart = TemplateView.as_view(template_name='admin/index1.html')
line_chart_json = LineChartJSONView.as_view()