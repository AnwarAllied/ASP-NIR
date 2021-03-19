from django.shortcuts import render
from django.views.generic import TemplateView
from .models import StaticModel,IngredientsModel

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


