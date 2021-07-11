from masterModelling.models import StaticModel,IngredientsModel
from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.utils import to_current_timezone

from django.template import loader
from django.contrib.flatpages.models import FlatPage
from .dataHandeller import datasheet4matching
from django.views.generic import TemplateView
# from django.db.models import Q
from django.contrib import messages
from .forms import MatchForm
from .admin import myMatchAdmin
from .models import Match, Owner

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
        uploaded,msg=datasheet4matching(file=dsFile, filename=str(request.FILES['select_a_spectrum']), owner_id=Owner.o.get_id(request.user))
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
        plot_update=self.request.GET.get('plot_update','')
        id=kwargs['id']
        method_id=kwargs['method_id']
        data = super().get_context_data()
        obj = Match.objects.get(id=id)
        method = StaticModel.objects.get(id=method_id)
        text =eval(method.profile)['titles']
        data['match_id']=id
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

        return data