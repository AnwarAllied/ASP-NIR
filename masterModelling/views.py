from django.shortcuts import render
from django.views.generic import TemplateView
from .models import StaticModel,IngredientsModel

class master_pca(TemplateView):
    template_name = 'change_list.html'

    def get_context_data(self, **kwargs):
        model = self.request.GET.get('model', '')
        data = super().get_context_data()
        data['staticModel'] = False

        return data
