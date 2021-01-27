from django.contrib import admin
from .models import Spectrum, NirProfile
from spectraModelling.models import Poly, Match
from spectraModelling.admin import myMatchAdmin, myPolyAdmin
from .forms import NirProfileForm
from django.contrib.auth.models import Group ,User
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from .dataHandeller import datasheet2spec
from django.contrib import messages
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.utils.translation import gettext_lazy as _
import pickle

# Define a new FlatPageAdmin
class myFlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )
    # to remove action plot:
    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))

class NirProfileAdmin(admin.ModelAdmin):
    form = NirProfileForm
    fieldsets = (
        (None, {
            'fields': ('title',) 
        }),
        ('NIR options', {
            'fields': ('nir_type', 'nir_method', 'nir_configuration')
        }),
        ('Figure', {
            'classes': ('collapse',),
            'fields': ('figure_id', 'figure_title', 'figure_caption', 'x_label', 'y_label', 'x_min', 'x_max','y_min', 'y_max')
        }),
        ('Reference', {
            'fields': ('reference_type', 'reference_title', 'reference_link')
        }),
        ('Included Spectra', {
            'classes': ('collapse',),
            'fields': ("upload_dataset",),
        }),
    )

    def response_change(self, request, obj, **kwargs):
        if 'upload_dataset' in request.FILES.keys():
            dsFile=request.FILES['upload_dataset'].file
            dsFile.seek(0)
            uploaded,msg=datasheet2spec(file=dsFile, pk=obj.pk, filename=str(request.FILES['upload_dataset']) )
            print(msg)
            if not uploaded:
                messages.error(request, 'Sorry, the uploaded file is not formated properly.')

        # print('pk',obj.pk)
        # print(dir(request))
        # print('post:',request.POST.items)
        # print(request.FILES['upload_dataset'].file)
        # print(dir(request.FILES['upload_dataset']))
        # print('file:',request.FILES['upload_dataset'])
        # print(kwargs)
        # with open('company_data.pkl', 'wb') as output:
        #     # company1 = Company('banana', 40)
        #     pickle.dump(request.FILES['upload_dataset'].file, output, pickle.HIGHEST_PROTOCOL)

        # with open('company_data.pkl', 'rb') as input:
        #     company1 = pickle.load(input)
        # pd.read_excel(request.FILES['upload_dataset'].file, index_col=False, error_bad_lines=False, encoding='utf-8')
        return super().response_change(request, obj, **kwargs)


class MyAdminSite(admin.AdminSite):
    default_site = 'myproject.admin.MyAdminSite'
    site_header = 'NIRvaScan - Allied Scientific Pro'
    site_title = 'NIR spectra'

    def export_as_json(self, request, queryset):
        response = HttpResponse(content_type="application/json")
        print(dir(response),'\n',response.content)
        serializers.serialize("json", queryset, stream=response)
        print(dir(response),'\n',response.content)
        return response

    def export_selected_objects(self, request, queryset):
        model=queryset.model.__name__
        selected = queryset.values_list('pk', flat=True)
        ct =eval(model+".objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in selected)))")
        
        return HttpResponseRedirect('/plot/?model=%s&ids=%s' % (
            model, ','.join(str(pk) for pk in selected),
        ))

    def plot_spectra(self, request, queryset):
        short_description = "Plot selected spectra"

    # plot_spectra.short_description = "Plot selected spectra"
    di1={'Poly':('plot_spectra',export_selected_objects)}
    actions = [di1['Poly']]+[('delete_selected', dict(admin.AdminSite().actions)['delete_selected'])]

class NoPlot(admin.ModelAdmin):
    # to remove action plot:
    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))

# to remove action plot:
def remove_action(response,remove = 'plot_spectra'):
    # response=super().changelist_view(request)
    if 'action_form' in response.context_data.keys():
        action_choices=response.context_data['action_form'].fields['action'].choices
        action_choices=[i for i in action_choices if i[0] != remove ]
        response.context_data['action_form'].fields['action'].choices = action_choices
    return response

admin_site = MyAdminSite(name='myadmin')
# Re-register FlatPageAdmin
# admin_site.unregister(FlatPage)
admin_site.register(FlatPage, myFlatPageAdmin)
admin_site.register(Group,NoPlot)
admin_site.register(User,NoPlot)
admin_site.register(Spectrum)
admin_site.register(NirProfile,NirProfileAdmin)
admin_site.register(Poly,myPolyAdmin)
admin_site.register(Match,myMatchAdmin)
# admin_site.register(NirProfileAdmin)