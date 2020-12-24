from django.contrib import admin
from .models import Spectrum, NirProfile
from django.contrib.auth.models import Group ,User
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q

class NirProfileAdmin(admin.ModelAdmin):
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
        # ('Included Spectra', {
        #     # 'classes': ('collapse',),
        #     'fields': (None,),
        # }),
    )


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