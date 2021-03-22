from django.shortcuts import render
from django.views.generic import TemplateView
from .models import StaticModel,IngredientsModel
from core.models import Spectrum, NirProfile
from chartjs.views.lines import BaseLineChartView

class master_pca(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        model = self.request.GET.get('model', '')

        data = super().get_context_data()

        data['model'] = model
        # data['index_text'] = 'test for master static'
        data['master_static_pca'] = True
        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = 'masterModelling' if (model == 'staticModel' or model == 'ingredientsModel') else 'core'
        data['verbose_name'] = model
        return data


class master_pls(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        model = self.request.GET.get('model', '')
        print('test master:', model)
        data = super().get_context_data()
        data['model'] = model
        # data['index_text'] = 'test for master static'
        data['master_static_pls'] = True
        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = 'masterModelling' if (model == 'staticModel' or model == 'ingredientsModel') else 'core'
        data['verbose_name'] = model
        return data

class master_pls_chart(BaseLineChartView):
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"})
        default_opt.update({'pointRadius': 5})
        return default_opt

    def spec2context(self, **kwargs):
        # model = self.request.GET.get('model', '')
        # mode = self.request.GET.get('mode', '')
        # model_id=self.request.GET.get('model_id','')
        # model_id= int(model_id) if model_id else model_id
        # ids = [i.id for i in Spectrum.objects.all()]
        # ids = list(map(int, self.request.GET.get('ids', '').split(',')))
        # self.request.session['model'] = model
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        spectra = Spectrum.objects.all()
        # print("spectra:",spectra)
        context.update({'Spectra': spectra})
        # context.update({'dic': dic})
        return context

    def get_labels(self):
        self.cont=self.spec2context()
        return self.get_providers()

    def get_providers(self):
        return [i.origin for i in self.cont['Spectra'].all()]

    # def get_data(self):
    #     trans=self.cont['trans']
    #     # l=len(trans.T)
    #     # if l<2:
    #     #     trans=np.array([list(range(len(trans[0]))),trans[0].tolist()])
    #     return [[{"x":a,"y":b}] for a,b in trans[:,:2]]#[{"x":1,"y":2},{"x":5,"y":4}],[{"x":3,"y":4},{"x":3,"y":1}]]#

