import json

from chartjs.colors import next_color

from core.models import Spectrum, NirProfile
from masterModelling.models import StaticModel,IngredientsModel
from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.utils import to_current_timezone

from django.template import loader
from django.contrib.flatpages.models import FlatPage

from predictionModel.models import PcaModel
from .dataHandeller import datasheet4matching
from django.views.generic import TemplateView
# from django.db.models import Q
from django.contrib import messages
from .forms import MatchForm
from .admin import myMatchAdmin
from .models import Match
from django.views.decorators.csrf import csrf_exempt
import re
# Create your views here.


def match(request):
    template = loader.get_template('admin/match.html')
    flat_page=FlatPage.objects.get(url= '/match/')
    context = {
        'has_permission': request.user.is_authenticated,
        'title': flat_page.title,
        'index_text' : flat_page.content,
        'form' : MatchForm,
        'figure_header': "Matching result:",
        'plot_mode': 'detail',
        'model':'Match',
        'ids': '8'
    }
    return HttpResponse(template.render(context, request))

# @csrf_exempt
# def get_match_upload(request):
    # print('get_upload_test:',request.get_full_path())
    # y_axis=request.GET.get('y_axis','')
    # # print('y_axis:',y_axis)
    # y_axis_n = request.POST.get('y_axis','')
    # xmin = request.POST.get('xmin','')
    # xmax = request.POST.get('xmax','')
    # s = Spectrum()
    # s.origin = 'test_upload_auto'
    # s.color = 'red'
    # s.y_axis = y_axis_n
    # s.x_range_max = xmax
    # s.x_range_min = xmin

    # for ISC SDK
    # file_name = request.POST.get('file_name','')
    # print('file_name:',file_name)
    # x_received = request.POST.get('x_data', '')
    # y_received = request.POST.get('y_data', '')
    # print('data:',x_received)
    # if file_name and x_received and y_received:
    #     x_received = x_received[1:-1].split(',')
    #     s.x_range_min = x_received[0]
    #     s.x_range_max = x_received[len(x_received) - 1]
    #     s.y_axis = str(y_received)[1:-1]
    #     s.origin = file_name
    # s.save()
    # msg = "Data successfully received by Nirvascan"
    # return HttpResponse(msg)

@csrf_exempt
def match_upload(request):
    print('file:',request.FILES.keys())
    print('content:', dir(request.FILES['form_field_name']))
    print('read:', request.FILES['form_field_name'].read())
    if 'select_a_spectrum' in request.FILES.keys():
        dsFile=request.FILES['select_a_spectrum'].file
        dsFile.seek(0)
        uploaded,msg=datasheet4matching(file=dsFile, filename=str(request.FILES['select_a_spectrum']))
        print('name :',str(request.FILES['select_a_spectrum']))
        if not uploaded:
            print('uploaded :',uploaded)
            messages.error(request, 'Sorry, the uploaded file is not formated properly.')
            return match(request)
        # '<path:object_id>/change/', wrap(self.change_view), name='%s_%s_change'  http://127.0.0.1:8000
        # return HttpResponseRedirect("%sadmin/spectraModelling/match/%d/change/" % (request.build_absolute_uri('/'),uploaded.id))
        return HttpResponseRedirect("%smatch/%d/method/%d" % (request.build_absolute_uri('/'),uploaded.id,2))
    else:
        messages.error(request, 'Sorry, nothing to upload.')
        return match(request)

class match_method(TemplateView):

    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        print(kwargs)
        plot_update=self.request.GET.get('plot_update','')
        id=kwargs['id']
        method_id=kwargs['method_id']
        data = super().get_context_data()
        obj = Match.objects.get(id=id)
        method = StaticModel.objects.last()
        text =eval(method.profile)['titles']
        data['id']=id
        data['obj_id']=method.id
        data['model'] = obj._meta.model_name
        data['match_master']=True
        data['master_static_pca'] = True
        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = "spectraModelling"
        data['verbose_name'] = 'Matching'
        data['figure_header']= 'Matching of unknown spectrum uploaded at ' + to_current_timezone(obj.created_at).__str__()[:-7]
        data['text']=text
        data['spec_num']=method.count
        data['group_num']=len(text)
        data['components']=method.n_comp
        if plot_update:
            print('_'*40)
            # cn=mpc.spec2context(self,**data)
            # print(cn)


        return data


