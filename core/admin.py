from django.contrib import admin
from .models import Spectrum, NirProfile
from .forms import NirProfileForm
from django.contrib.auth.models import Group ,User
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from .dataHandeller import datasheet2spec
import pickle

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
        # print('pk',obj.pk)
        # print(dir(request))
        # print('post:',request.POST.items)
        # print(request.FILES['upload_dataset'].file)
        # print(dir(request.FILES['upload_dataset']))
        # print('file:',request.FILES['upload_dataset'])
        # print(kwargs)

        dsFile=request.FILES['upload_dataset'].file
        dsFile.seek(0)
        message=datasheet2spec(file=dsFile, pk=obj.pk, filename=str(request.FILES['upload_dataset']) )
        print(message)
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
        selected = queryset.values_list('pk', flat=True)
        ct = Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in selected)))
        return HttpResponseRedirect('/plot/?model=%s&ids=%s' % (
            ct.model.__name__, ','.join(str(pk) for pk in selected),
        ))

    def plot_spectra(self, request, queryset):
        # queryset.update(x_range_min='600')
        pass

    plot_spectra.short_description = "Plot selected spectra"

    actions = [('plot_spectra',export_selected_objects),('delete_selected', dict(admin.AdminSite().actions)['delete_selected'])]

admin.site.register(Spectrum)
admin.site.register(NirProfile,NirProfileAdmin)

admin_site = MyAdminSite(name='myadmin')
admin_site.register(Group)
admin_site.register(User)
admin_site.register(Spectrum)
admin_site.register(NirProfile,NirProfileAdmin)
# admin_site.register(NirProfileAdmin)