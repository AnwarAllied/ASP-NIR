from django.contrib import admin

from .models import Spectrum, NirProfile
from spectraModelling.models import Poly, Match
from predictionModel.admin import PcaModel, PlsModel, myPcaModelAdmin, myPlsModelAdmin
from spectraModelling.admin import myMatchAdmin, myPolyAdmin

from .forms import NirProfileForm, SpectrumForm
from django.contrib.auth.models import Group,User
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from .dataHandeller import datasheet2spec
from django.contrib import messages
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.utils.translation import gettext_lazy as _
import re
# import pickle


# class FlatInline(admin.TabularInline):
#     model = FlatPage
#     verbose_name = "Static page"

# Define a new FlatPageAdmin
class myFlatPageAdmin(FlatPageAdmin):
    view_on_site = False
    # inlines = [FlatInline, ]
    verbose_name = "Static page"
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

class SpectrumAdmin(admin.ModelAdmin):
    view_on_site = False
    list_display = ('__str__','spec_image')
    # readonly_fields = ('spec_image',)
    def save_model(self, request, obj, form, change):
        # change the delimiter to ", "
        delimiter=re.findall("[^\d\,\.\- ]+",obj.y_axis[:100])
        if delimiter:
            print('Delimiter changed from: %r' % delimiter[0])
            obj.y_axis=re.sub(delimiter[0],', ',obj.y_axis)
        super().save_model(request, obj, form, change)

        # to disable 1 spectrum selection for PCA and PLS model
    def changelist_view(self, request, extra_context=None):
        is_single_selected, message=single_item_selected(request, *['PCA_model','PLS_model'])
        if is_single_selected:
            self.message_user(request, message, messages.WARNING)
            return HttpResponseRedirect(request.get_full_path())
        else:
            return super().changelist_view(request, extra_context=None)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data()
    #     print(context)

class NirProfileAdmin(admin.ModelAdmin):
    view_on_site = False
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
    view_on_site = False

    def export_as_json(self, request, queryset):
        response = HttpResponse(content_type="application/json")
        print(dir(response),'\n',response.content)
        serializers.serialize("json", queryset, stream=response)
        print(dir(response),'\n',response.content)
        return response

    def plot_export_selected_objects(self, request, queryset):
        model=queryset.model.__name__
        selected = queryset.values_list('pk', flat=True)
        ct =eval(model+".objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in selected)))")
        return HttpResponseRedirect('/plot/?model=%s&ids=%s' % (
            model, ','.join(str(pk) for pk in selected),
        ))

    def pca_export_selected_objects(self, request, queryset):
        model=queryset.model.__name__
        selected = queryset.values_list('pk', flat=True)
        ct =eval(model+".objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in selected)))")
        return HttpResponseRedirect('/pca/?model=%s&ids=%s' % (
            model, ','.join(str(pk) for pk in selected),
        ))

    def pls_export_selected_objects(self, request, queryset):
        model=queryset.model.__name__
        selected = queryset.values_list('pk', flat=True)
        ct =eval(model+".objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in selected)))")
        return HttpResponseRedirect('/pls/?model=%s&ids=%s' % (
            model, ','.join(str(pk) for pk in selected),
        ))

    def plot_spectra(self, request, queryset):
        short_description = "Plot selected spectra"

    def pca_model(self, request, queryset):
        short_description = "PCA of selected spectra"

    def pls_model(self, request, queryset):
        short_description = "PLS of selected spectra"

    # plot_spectra.short_description = "Plot selected spectra"
    di1={'Poly':('Plot_spectra',plot_export_selected_objects)}
    di2={'PCA':('PCA_model',pca_export_selected_objects)}
    di3 = {'PLS': ('PLS_model', pls_export_selected_objects)}
    actions = [di1['Poly'],di2['PCA'],di3['PLS']]+[('delete_selected', dict(admin.AdminSite().actions)['delete_selected'])]

class NoPlot(admin.ModelAdmin):
    view_on_site = False

    # to remove action plot:
    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))

# to remove action plot:
def remove_action(response,remove = ['Plot_spectra','PCA_model', 'PLS_model']):
    # response=super().changelist_view(request)
    if 'action_form' in response.context_data.keys():
        action_choices=response.context_data['action_form'].fields['action'].choices
        action_choices=[i for i in action_choices if i[0] not in remove ]
        response.context_data['action_form'].fields['action'].choices = action_choices
    return response

 # to disable single spectrum selection for PCA and PLS model
def single_item_selected(request,*action_models):
    keys=request.POST.keys()
    if request.method == 'POST' and 'action' in keys and '_selected_action' in keys:
        action = request.POST['action']
        selected = request.POST.__str__().split("_selected_action': ['")[1].split("']")[0].split("', '")
        if action in action_models and len(selected) < 2:
            msg = "More than one item must be selected in order to perform modeling actions on them. No action have been performed."
            return True, msg

    return False, ''

# def delete_selected_items(response):


admin_site = MyAdminSite(name='myadmin')
# Re-register FlatPageAdmin
# admin_site.unregister(FlatPage)
admin_site.register(FlatPage, myFlatPageAdmin)
admin_site.register(Group,NoPlot)
admin_site.register(User,NoPlot)
admin_site.register(Spectrum,SpectrumAdmin)
admin_site.register(NirProfile,NirProfileAdmin)
admin_site.register(Poly,myPolyAdmin)
admin_site.register(Match,myMatchAdmin)
admin_site.register(PlsModel,myPlsModelAdmin)
admin_site.register(PcaModel,myPcaModelAdmin)
# admin_site.register(NirProfileAdmin)