from django.contrib import admin
from spectraModelling.models import Poly, Match
# Register your models here.

class myMatchAdmin(admin.ModelAdmin):
    view_on_site = False
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = Match.objects.get(id=object_id)
        extra_context['match_data'] = obj
        extra_context['model']='Match'
        extra_context['ids']=object_id
        extra_context['plot_mode']='detail'
        extra_context['title']='Matching unknown spectrum:'
        extra_context['index_text']= 'Matching unknown spectrum with order:%d and MSE:%f' % (obj.order, obj.mse)
        rn= super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
        return rn


class myPolyAdmin(admin.ModelAdmin):
    view_on_site = False
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = Poly.objects.get(pk=object_id)
        extra_context['poly_data'] = obj
        extra_context['model']='Poly'
        extra_context['ids']=object_id
        extra_context['plot_mode']='detail'
        extra_context['title']='Poly-model and matched spectra:'
        extra_context['index_text']= 'Polynomial modeled spectrum of %s, with order:%d and MSE:%f' % (obj.spectrum.origin, obj.order, obj.mse)
        rn= super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
        # print('object_id:',object_id)
        # print('run:',rn.template_name)
        # print('item:',rn.items())
        # print('self:',self.change_form_template)
        # print('Poly detail:',request.get_full_path())
        return rn