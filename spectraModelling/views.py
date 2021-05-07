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

def match_upload(request):
    print('file:',request.FILES.keys())
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
        method = StaticModel.objects.get(id=method_id)
        text =eval(method.profile)['titles']
        data['id']=id
        data['obj_id']=method_id
        data['model'] = obj._meta.model_name
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

class match_specific_pca(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        spec_ids=eval(self.request.GET.get('spec_ids',''))
        nir_ids=[Spectrum.objects.get(id=i).nir_profile_id for i in spec_ids if i]
        titles=[NirProfile.objects.get(id=i).title for i in set(nir_ids) if i]
        spectra=[Spectrum.objects.get(id=i) for i in spec_ids if i]
        pca_id=self.request.GET.get('pca_id','')
        colors, co_titles, color_set = obtain_colors(titles)
        spectra_m = {'ids': spec_ids, 'titles': [i.origin for i in spectra], 'colors': colors, 'color_titles': co_titles}
        profile = {'ids': nir_ids, 'titles': titles, 'color_set': color_set}
        method=PcaModel.objects.get(id=pca_id)
        trans = '[' + method.transform + ']'
        master_pca = StaticModel()
        master_pca.title = method.__str__()
        master_pca.spectra = json.dumps(spectra_m)
        master_pca.profile = profile
        master_pca.count = len(spectra)
        master_pca.score = method.score
        master_pca.n_comp = method.order
        master_pca.trans = trans
        master_pca.preprocessed = json.dumps({})
        master_pca.applied_model = method.__str__()
        master_pca.save()

        id = kwargs['id']
        spec_uploaded = Match.objects.get(id=id)
        text=method.__str__()
        data['id'] = id
        data['obj_id']=StaticModel.objects.last().id
        data['pca_id'] =pca_id
        data['model'] =text
        data['master_static_pca'] = True
        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = "spectraModelling"
        data['verbose_name'] = 'Matching'
        data['figure_header'] = 'Matching of unknown spectrum uploaded at ' + to_current_timezone(
            spec_uploaded.created_at).__str__()[:-7]
        data['text'] = text
        data['spec_num'] =len(spectra)
        data['group_num'] =len(titles)
        data['components'] = method.order
        self.request.session['pca_spec_ids']=spec_ids
        return data

def obtain_colors(titles):
    color_set={ 'wheat':'255, 165, 0', 'durum':'235, 97, 35', 'narcotic':'120,120,120', 'tomato':'216, 31, 42', 'garlic':'128,128,128', 'grape':'0, 176, 24', 'other': '241 170 170' }
    # sp=kwargs['spectra']
    # s1=str(sp['titles']).lower()
    s1=str(titles).lower()
    s2=re.sub('[^\w ]+','',s1)
    s3=re.sub(r'\d+|\b\w{1,2}\b','',s2)
    s4=re.sub('brix|protein|moisture|data|test|validation|calibration|asp','',s3)
    s5=re.sub(' +',' ',s4)
    s6=re.findall('\w{3,}',s5)
    s7={s6.count(i):i for i in list(set(s6))}
    ls=sorted(s7.keys(),reverse=True)
    gp=[]
    for i in eval(s1):
        has_origin=False
        for j in ls:
            if s7[j] in i and not has_origin:
                has_origin=True
                gp.append(s7[j])
        if not has_origin:
            gp.append('other')
    co=[]
    ti=[]
    ls=list(color_set.keys())
    color_dict={}
    for i in gp:
        has_origin=False
        for j in ls:
            if j in i and not has_origin:
                has_origin=True
                co.append('rgba(%s, 1)' % color_set[j])
                ti.append(j)
                color_dict.update({j:color_set[j]})
        if not has_origin:
            new_color=str(tuple(next(next_color())))
            co.append('rgba%s' %new_color)
            ti.append(i)
            color_set.update({i:new_color[1:-1]})
            color_dict.update({i:new_color[1:-1]})
    return co, ti, color_dict