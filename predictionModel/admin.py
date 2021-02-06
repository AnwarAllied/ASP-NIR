from django.contrib import admin
# from spectraModelling.models import Poly, Match
from predictionModel.models import PcaModel

class myPcaAdmin(admin.ModelAdmin):
    view_on_site = False

    
    # to disable 1 spectrum selection for PCA and PLS model
    def response_action(self, request, queryset):
        print('action resp.:',request.POST.__dict__)
        print('queryset :',queryset.__dict__)
        return super().response_action(request, queryset)
        
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     obj = Match.objects.get(id=object_id)
    #     extra_context['match_data'] = obj
    #     extra_context['model']='Match'
    #     extra_context['ids']=object_id
    #     extra_context['plot_mode']='detail'
    #     extra_context['title']='Matching unknown spectrum:'
    #     extra_context['index_text']= 'Matching unknown spectrum with order:%d and MSE:%f' % (obj.order, obj.mse)
    #     rn= super().change_view(
    #         request, object_id, form_url, extra_context=extra_context,
    #     )
    #     return rn
    #     # to remove action plot:

    # def changelist_view(self, request):
    #     return remove_action(super().changelist_view(request))

# Register your models here.

