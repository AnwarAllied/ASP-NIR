from django.contrib import admin
from .models import Spectrum, NirProfile
from predictionModel.admin import PcaModel, myPcaModelAdmin, PlsModel, myPlsModelAdmin
from spectraModelling.admin import Poly, Match, myMatchAdmin, myPolyAdmin
from masterModelling.admin import StaticModel, IngredientsModel, StaticModelAdmin, IngredientsModelAdmin
from preprocessingFilters.admin import *

from ASP_NIR.settings import DROPBOX_ACCESS_TOKEN
from .forms import NirProfileForm, SpectrumForm
from django.contrib.auth.models import Group ,User
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from .dataHandeller import datasheet2spec
from django.contrib import messages
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.templatetags.admin_list import results
import re, json, dropbox, requests


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
    form = SpectrumForm
    # list_per_page = 300
    # change_list_template = 'admin/spectra_display_list.html'
    list_display = ('__str__','spec_image')

    def save_model(self, request, obj, form, change):
        # change the delimiter to ", "
        delimiter=re.findall("[^\d\,\.\- E]+",obj.y_axis[:100])
        if delimiter:
            # print('Delimiter changed from: %r' % delimiter[0])
            obj.y_axis=re.sub(delimiter[0],', ',obj.y_axis)
        super().save_model(request, obj, form, change)
        # Handel Dropbox images:
        if request.FILES:
            obj.pic_path = getDropboxImgUrl()  # assign pic url on dropbox to the spectrum
            
            '''
            because the uploaded picture has a new url on dropbox, we have to 
            update the pic_path of all the spectra with the same spec_pic
            '''
            spectra = Spectrum.objects.all()
            for i in spectra:
                if i.spec_pic and i.spec_pic == obj.spec_pic:
                    i.pic_path = obj.pic_path
                    i.save()
            obj.save()
        
        
    def changelist_view(self, request, extra_context=None):

        # to disable 1 spectrum selection for PCA and PLS model
        is_single_selected, message=single_item_selected(request, ['PCA_model','PLS_model'])
        if is_single_selected:
            self.message_user(request, message, messages.WARNING)
            return HttpResponseRedirect(request.get_full_path())
        else:
            # cutomize the changelist page of spectrum
            # response = super().changelist_view(request, extra_context=None)
            response = remove_action(super().changelist_view(request, extra_context=None), remove = ['Download_as_excel_file'])
            try:
                qs = response.context_data['cl'].queryset  # get_queryset
            except (AttributeError, KeyError):
                return response
            
            if 'smallPic' in request.POST.keys():
                response.context_data['is_big_pic'] = False
            else:
                response.context_data['is_big_pic'] = True

            # To over-ride change-list-results:
            # if 'context_data' in dir(response):
            #     if 'cl' in response.context_data.keys():
            #         cl=response.context_data['cl']
            #         qs = cl.queryset
            #         result=list(results(cl))   # this is the results found in the changelist_results html.
            #         response.context_data['items']=[[i for i in r]+[q.spec_image()] for r,q in zip(result,qs.all())]
            return response


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
            'fields': ("upload_dataset","upload_picture"),
        }),
    )

    def response_change(self, request, obj, **kwargs):
        if 'upload_picture' in request.FILES.keys():
            dsFile=request.FILES['upload_picture']
            elm=obj.spectrum_set.all()[0]
            elm.spec_pic.save(dsFile.name,dsFile)
            pic_path = getDropboxImgUrl()
            elm.pic_path=pic_path
            elm.save()
            for elem in obj.spectrum_set.all()[1:]:
                elem.spec_pic=elm.spec_pic
                elem.pic_path=pic_path
                elem.save()
            messages.success(request, "Picture set to Spectra" )

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

        # to remove action Download:
    def changelist_view(self, request):
        return remove_action(super().changelist_view(request), remove = ['Download_as_excel_file'])

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

    def xlsx_export_selected_objects(self, request, queryset):
        model=queryset.model.__name__
        selected = queryset.values_list('pk', flat=True)
        ct =eval(model+".objects.filter(eval('|'.join('Q(pk='+str(pk)+')' for pk in selected)))")
        return HttpResponseRedirect('/xlsx/?model=%s&ids=%s' % (
            model, ','.join(str(pk) for pk in selected),
        ))

    def plot_spectra(self, request, queryset):
        short_description = "Plot selected spectra"

    def pca_model(self, request, queryset):
        short_description = "PCA of selected spectra"

    def pls_model(self, request, queryset):
        short_description = "PLS of selected spectra"

    def download_xlsx(self, request, queryset):
        short_description = "Download selected spectra as xlsx"

    # plot_spectra.short_description = "Plot selected spectra"
    di1={'Poly':('Plot_spectra',plot_export_selected_objects)}
    di2={'PCA':('PCA_model', pca_export_selected_objects)}
    di3 = {'PLS': ('PLS_model', pls_export_selected_objects)}
    di4 = {'XISX': ('Download_as_excel_file', xlsx_export_selected_objects)}
    actions = [di1['Poly'],di2['PCA'],di3['PLS'],di4['XISX']]+[('delete_selected', dict(admin.AdminSite().actions)['delete_selected'])]

class NoPlot(admin.ModelAdmin):
    view_on_site = False

    # to remove action plot:
    def changelist_view(self, request):
        return remove_action(super().changelist_view(request))

# to remove action plot:
def remove_action(response,remove = ['Plot_spectra','PCA_model','PLS_model', 'Download_as_excel_file']):
    # response=super().changelist_view(request)
    if 'context_data' in dir(response):
        if 'action_form' in response.context_data.keys():
            action_choices=response.context_data['action_form'].fields['action'].choices
            action_choices=[i for i in action_choices if i[0] not in remove ]
            response.context_data['action_form'].fields['action'].choices = action_choices
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

def getDropboxImgUrl():
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    imgs=[i.name for i in dbx.files_list_folder('/nirpics').entries]
    url=''
    if imgs!=[] :
        img=imgs[len(imgs)-1]
        url = "https://api.dropboxapi.com/2/sharing/create_shared_link"
        headers = {"Authorization": "Bearer "+DROPBOX_ACCESS_TOKEN,
                   "Content-Type": "application/json"}
        data = {"path": "/nirpics/"+img}
        r = requests.post(url, headers=headers, data=json.dumps(data))
        rn = json.loads(r.text)
        url = rn['url'].replace('www.dropbox.com', 'dl.dropboxusercontent.com')
        url = url.replace('?dl=0', '')
    return url

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
admin_site.register(SgFilter,mySgFilterAdmin)
admin_site.register(StaticModel,StaticModelAdmin)
admin_site.register(IngredientsModel,IngredientsModelAdmin)
# admin_site.register(NirProfileAdmin)