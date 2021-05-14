from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from .models import StaticModel, IngredientsModel
from django.urls import path, reverse


# Register your models here.
class StaticModelAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):

        obj=StaticModel.objects.get(id=object_id)
        if 'PCA' in obj.title:
            url='/master_static_pca?id=%s' % object_id
        elif 'PLS' in obj.title:
            url='/master_static_pls?id=%s' % object_id
        elif 'LDA' in obj.title:
            url='/master_static_pca?id=%s' % object_id
        return HttpResponseRedirect(url)


    def changelist_view(self, request, extra_context=None):
        return remove_action(super().changelist_view(request))


class IngredientsModelAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        return remove_action(super().changelist_view(request))




def remove_action(response,remove = ['Plot_spectra', 'PCA_model','PLS_model']):
    if 'context_data' in dir(response):
        if 'action_form' in response.context_data.keys():
            action_choices=response.context_data['action_form'].fields['action'].choices
            action_choices=[i for i in action_choices if i[0] not in remove ]
            response.context_data['action_form'].fields['action'].choices = action_choices
    return response