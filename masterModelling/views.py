from django.shortcuts import render
from django.views.generic import TemplateView

from .models import StaticModel,IngredientsModel
from core.models import Spectrum, NirProfile
from chartjs.views.lines import BaseLineChartView
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from predictionModel.models import normalize_y
import numpy as np

class master_pca(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        s = Spectrum.objects.all()
        n = NirProfile.objects.all()
        text = [i.title for i in n]
        data['model'] = 'StaticModel'
        data['index_text'] = 'master pca'
        data['master_static_pca'] = True
        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = 'masterModelling'
        data['verbose_name'] = 'MasterModellingPca'
        data['figure_header']='Master model for PCA'
        data['text']=text
        data['spec_num']=len(s)
        data['group_num']=len(text)
        data['components']=2
        # data['score']=self.request.session['score']
        return data

class master_pca_chart(BaseLineChartView):
    def get_context_data(self, **kwargs):
        content = {"labels": self.get_labels()}
        datasets=self.get_datasets()
        obj=datasets[len(datasets)-1]
        # print(obj)
        obj['label']='Latest uploaded spectrum: '+obj['label']
        # print(obj['label'])
        content.update({"datasets": datasets})
        context=self.cont
        context.update(content)
        return context

    def spec2context(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        spectra = Spectrum.objects.all()
        Y=[i.y() for i in spectra]
        Y=normalize_y(Y)
        pca=PCA(n_components=2)
        pca.fit(Y)
        trans=pca.transform(Y)
        # try:  # incase len(Y)<=2:
        #     score = pca.score(Y)
        # except ValueError:
        #     score = 00
        # self.request.session['score']=score
        # self.request.session['trans']=trans
        context.update({'spectra': spectra, 'trans':trans})
        return context

    def get_labels(self):
        self.cont = self.spec2context()
        return self.get_providers()

    def get_providers(self):
        messages=self.close_to()
        return [i.origin + j for i, j in zip(self.cont['spectra'].all(),messages)]

    def close_to(self):
        spectra = self.cont['spectra']
        trans = self.cont['trans']
        messages = []
        distances=[[((i[0]-j[0])**2 + (i[1]-j[1])**2)**0.5 for i in trans] for j in trans]
        for distance in distances:
            n_distance=sorted(distance)  # sort
            # indices = [i for i, x in enumerate(distance) if x == distance[1]] # find all indices
            e_index=distance.index(n_distance[1])  # [0] -> itself, find the index of the shortest distance
            spectrum = spectra[e_index]  # find the nearest spectrum
            # print('debug:',spectrum)
            # save 3 nearest spectra in the session
            nearest_spectra_ids = [spectrum.id, spectra[distance.index(n_distance[2])].id, spectra[distance.index(n_distance[3])].id]
            self.request.session['nearest_spectra_ids'] = nearest_spectra_ids
            if spectrum.nir_profile_id:
                s = NirProfile.objects.get(id=spectrum.nir_profile_id)
                if s:
                    messages.append(' belongs or is close to ' + s.title)
            else:
                messages.append(' is close to ' + spectrum.origin)
        return messages

    def get_data(self):
        trans = self.cont['trans']
        return [[{"x":a,"y":b}] for a,b in trans[:,:2]]

class master_pca_element_chart(BaseLineChartView):
    template_name = 'admin/index_plot.html'
    def get_context_data(self, **kwargs):
        data=super().get_context_data()
        data['master_pca_element'] = True

    def spec2context(self,**kwargs):
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        id=self.request.GET.get('id','')
        spectrum=Spectrum.objects.get(id=id)
        nearest_spectra_ids=self.request.session['nearest_spectra_ids']
        spectra=[Spectrum.objects.get(id=i) for i in nearest_spectra_ids]
        spectra.append(spectrum)
        context.update({'spectra':spectra})
        return context
        # print(spectra)

    def get_labels(self):
        self.cont = self.spec2context()
        x=self.cont['spectra'][0].x()
        x = np.unique((np.round(x / 50) * 50).astype(int))
        self.cont['x_length'] = len(x)
        return x.tolist()

    def get_providers(self):
        return [i.label() for i in self.cont['spectra']]

    def get_data(self):
        x_length=self.cont['x_length']
        return [[i.y().tolist()[a] for a in np.linspace(0, len(i.y().tolist()) - 1, x_length).astype(int)] for i in
                self.cont['spectra']]

#
# class master_pls(TemplateView):
#     template_name = 'admin/index_plot.html'
#
#     def get_context_data(self, **kwargs):
#         model = self.request.GET.get('model', '')
#         print('test master:', model)
#         data = super().get_context_data()
#         data['model'] = model
#         # data['index_text'] = 'test for master static'
#         data['master_static_pls'] = True
#         data['has_permission'] = self.request.user.is_authenticated
#         data['app_label'] = 'masterModelling' if (model == 'staticModel' or model == 'ingredientsModel') else 'core'
#         data['verbose_name'] = model
#         return data
#
# class master_pls_chart(BaseLineChartView):
#     def get_dataset_options(self, index, color):
#         default_opt = super().get_dataset_options(index, color)
#         default_opt.update({"fill": "false"})
#         default_opt.update({'pointRadius': 5})
#         return default_opt
#
#     def spec2context(self, **kwargs):
#         # model = self.request.GET.get('model', '')
#         # mode = self.request.GET.get('mode', '')
#         # model_id=self.request.GET.get('model_id','')
#         # model_id= int(model_id) if model_id else model_id
#         # ids = [i.id for i in Spectrum.objects.all()]
#         # ids = list(map(int, self.request.GET.get('ids', '').split(',')))
#         # self.request.session['model'] = model
#         context = super(BaseLineChartView, self).get_context_data(**kwargs)
#         spectra = Spectrum.objects.all()
#         # print("spectra:",spectra)
#         context.update({'Spectra': spectra})
#         return context
#
#     def get_labels(self):
#         self.cont=self.spec2context()
#         return self.get_providers()
#
#     def get_providers(self):
#         return [i.origin for i in self.cont['Spectra'].all()]
#
#     def close_to(self):
#         pass
#
#
#     def get_data(self):
#         pass
#
# class master_pls_element_chart(BaseLineChartView):
#     pass