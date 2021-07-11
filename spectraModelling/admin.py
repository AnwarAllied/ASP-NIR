from django.contrib import admin
from spectraModelling.models import Poly, Match, Owner
from django.shortcuts import redirect
from django.contrib.admin.templatetags.admin_list import results
from django.http import HttpResponseRedirect
from django.contrib import messages
# from core.admin import remove_action
# Register your models here.

class myMatchAdmin(admin.ModelAdmin):
    view_on_site = False
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # extra_context = extra_context or {}
        # obj = Match.objects.get(id=object_id)
        # extra_context['match_data'] = obj
        # extra_context['obj_id'] = 2
        # extra_context['model']='Match'
        # extra_context['ids']=object_id
        # extra_context['plot_mode']='detail'
        # extra_context['title']='Matching unknown spectrum:'
        # extra_context['index_text']= 'Matching unknown spectrum with order:%d and MSE:%f' % (obj.order, obj.mse)
        # rn= super().change_view(
        #     request, object_id, form_url, extra_context=extra_context,
        # )
        return redirect('spectraModelling:method', id=object_id, method_id=2)#rn
        # to remove action plot:

    def changelist_view(self, request, extra_context=None):
        # to disable 1 spectrum selection for PCA and PLS model
        is_single_selected, message=single_item_selected(request, ['PCA_model','PLS_model'])
        if is_single_selected:
            self.message_user(request, message, messages.WARNING)
            return HttpResponseRedirect(request.get_full_path())
        else:
            response = remove_action(super().changelist_view(request), remove = ['Download_as_excel_file'])
            response = owner_change_list(request,response)
        return response


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
    
    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))



# to remove unwanted actions:
def remove_action(response,remove = ['PCA_model','PLS_model','Download_as_excel_file']):
    if 'context_data' in dir(response):
        if 'action_form' in response.context_data.keys():
            action_choices=response.context_data['action_form'].fields['action'].choices
            action_choices=[i for i in action_choices if i[0] not in remove ]
            response.context_data['action_form'].fields['action'].choices = action_choices
    return response

def owner_change_list(request,response):
 # To over-ride change-list-results:
    if 'context_data' in dir(response) and any(request.user.groups.all()):
        if 'cl' in response.context_data.keys():
            user=request.user
            if user.groups.first().name == 'customer':
                owner_id = Owner.o.get_id(user)
                p=request.GET.get('p','')
                p= int(p) if p else ''
                cl=response.context_data['cl']
                qs = cl.root_queryset.filter(owner_id__in=[owner_id]).order_by('-id')
                lpp=cl.list_per_page
                if p:
                    cl.result_list=qs[0+(p*lpp):lpp+(p*lpp)]
                else:
                    cl.result_list=qs[:lpp]
                cl.queryset=qs
                cl.result_count=qs.count()
                cl.full_result_count=qs.count()
                cl.paginator.object_list=qs
                cl.paginator.count=qs.count()
                cl.paginator.num_pages=0 if qs.count()<=lpp else round(qs.count()/lpp)+1
                cl.has_filters=False
                result=list(results(cl))[1:6]   # this is the results found in the changelist_results html.
                response.context_data['items']=result#[[i for i in r] for r,q in zip(result,qs.all())]

    return response

# to disable single spectrum selection for PCA and PLS model
def single_item_selected(request, action_model):
    keys=request.POST.keys()
    if request.method == 'POST' and 'action' in keys and '_selected_action' in keys:
        action = request.POST['action']
        selected = request.POST.__str__().split("_selected_action': ['")[1].split("']")[0].split("', '")
        if action in action_model and len(selected) < 2:
            msg = "More than one item must be selected in order to perform modeling actions on them. No action have been performed."
            return True, msg

    return False, ''