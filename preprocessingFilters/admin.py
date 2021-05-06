from django.contrib import admin
from .models import SgFilter
from .forms import SgFilterForm

class mySgFilterAdmin(admin.ModelAdmin):
    form = SgFilterForm
    def save_model(self, request, obj, form, change):
        # add y_axis
        ids=request.POST.getlist('nirprofile','')
        ids=list(map(int,ids)) if ids else None
        # print(ids)
        obj.obtain(ids=ids)
        # print('obj:',obj.y_axis[:100])
        super().save_model(request, obj, form, change)

    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))

# to remove unwanted actions:
def remove_action(response,remove = ['PCA_model',]):
    if 'context_data' in dir(response):
        if 'action_form' in response.context_data.keys():
            action_choices=response.context_data['action_form'].fields['action'].choices
            action_choices=[i for i in action_choices if i[0] not in remove ]
            response.context_data['action_form'].fields['action'].choices = action_choices
    return response