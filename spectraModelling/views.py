from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.flatpages.models import FlatPage
from .dataHandeller import datasheet4matching
# from django.db.models import Q
from django.contrib import messages
from .forms import MatchForm
from .admin import myMatchAdmin
# Create your views here.


def match(request):
    template = loader.get_template('admin/match.html')
    flat_page=FlatPage.objects.get(pk=2)
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
        return HttpResponseRedirect("%sadmin/spectraModelling/match/%d/change/" % (request.build_absolute_uri('/'),uploaded.id))
    else:
        messages.error(request, 'Sorry, nothing to upload.')
        return match(request)