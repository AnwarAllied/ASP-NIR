from django.contrib import admin
# from spectraModelling.models import Poly, Match
from predictionModel.models import PcaModel, PlsModel
from core.models import Spectrum, NirProfile
from spectraModelling.models import Poly
from predictionModel.forms import PcaMatchForm

class myPcaModelAdmin(admin.ModelAdmin):
    view_on_site = False
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = PcaModel.objects.get(id=object_id)
        extra_context['form'] = PcaMatchForm
        extra_context['pca_data'] = obj
        extra_context['model']='PcaModel'
        extra_context['ids']=object_id
        extra_context['plot_mode']='detail'
        extra_context['title']='PCA Model:'
        extra_context['index_text']= 'Calibration set of %s of maximum likelihood' % (obj.__str__())
        # extra_context['group']=[{'id':1,'name':'Narcotic', 'spectra':[{'id':1,'origin':'wheat_1'},{'id':2,'origin':'wheat_2'}]},{'id':2,'name':'Grape', 'spectra':[{'id':1,'origin':'wheat_3'},{'id':2,'origin':'wheat_4'}]}]
        extra_context['group']= profile2group(NirProfile)
        
        rn= super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
        return rn
        # to remove action plot:

    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))


class myPlsModelAdmin(admin.ModelAdmin):
    view_on_site = False
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = PlsModel.objects.get(id=object_id)
        extra_context['pls_data'] = obj
        extra_context['model']='PlsModel'
        extra_context['ids']=object_id
        extra_context['plot_mode']='detail'
        extra_context['title']='PLS model:'
        extra_context['index_text']= 'Calibration set of %s of the model' % (obj.__str__())
        extra_context['group'] = profile2group(NirProfile)
        extra_context['pls_modeling'] = True

        rn= super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
        # print('object_id:',object_id)
        # print('run:',rn.template_name)
        # print('item:',rn.items())
        # print('self:',self.change_form_template)
        # print('Poly detail:',request.get_full_path())
        return rn
    
    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))



# to remove unwanted actions:
def remove_action(response,remove = ['Plot_spectra','PCA_model','PLS_model']):
    if 'context_data' in dir(response):
        if 'action_form' in response.context_data.keys():
            action_choices=response.context_data['action_form'].fields['action'].choices
            action_choices=[i for i in action_choices if i[0] not in remove ]
            response.context_data['action_form'].fields['action'].choices = action_choices
    return response

def profile2group(profile):
    gp=[{'id':i.id,'name':i.title, 'spectra': [{'id':j.id,'origin':j.origin} for j in i.spectrum_set.all()]} for i in profile.objects.all() if i.spectrum_set.count()>0]
    # include spectra with no profiles:
    gp.append({'id':'O','name':'Others','spectra':[{'id':j.id,'origin':j.origin} for j in Spectrum.objects.filter(nir_profile=None)]})
    return gp