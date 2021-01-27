from django.contrib import admin
from spectraModelling.models import Poly, Match
# Register your models here.

class myMatchAdmin(admin.ModelAdmin):

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['match_data'] = Match.objects.get(id=object_id)
        extra_context['model']='Match'
        extra_context['ids']=object_id
        extra_context['plot_mode']='detail'
        extra_context['title']='Matching unknown spectrum:'
        rn= super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
        print('object_id:',object_id)
        print('run:',rn.template_name)
        print('item:',rn.items())
        print('self:',self.change_form_template)
        print('matching detail:',request.get_full_path())
        return rn


class myPolyAdmin(admin.ModelAdmin):

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['poly_data'] = Poly.objects.get(pk=object_id)
        extra_context['model']='Poly'
        extra_context['ids']=object_id
        extra_context['plot_mode']='detail'
        extra_context['title']='Poly-model and matchced spectra:'
        rn= super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
        print('object_id:',object_id)
        print('run:',rn.template_name)
        print('item:',rn.items())
        print('self:',self.change_form_template)
        print('Poly detail:',request.get_full_path())
        return rn