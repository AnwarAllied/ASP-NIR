from django.shortcuts import render
from django.views.generic import TemplateView
import re
from .models import StaticModel,IngredientsModel
from core.models import Spectrum, NirProfile
from chartjs.views.lines import BaseLineChartView
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from predictionModel.models import normalize_y
import numpy as np
from spectraModelling.models import Match

class master_pca(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        s = Spectrum.objects.all()
        n = NirProfile.objects.all()
        text = [i.title for i in n]
        data['model'] = 'StaticModel'
        # data['index_text'] = 'master pca'
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
        static_model=StaticModel.objects.first()
        static_model.component=str(pca.components_.tolist())[1:-1]
        static_model.save()
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
        nearest_spectra_ids_all = []
        for distance in distances:
            n_distance=sorted(distance)  # sort
            # indices = [i for i, x in enumerate(distance) if x == distance[1]] # find all indices
            e_index=distance.index(n_distance[1])  # [0] -> itself, find the index of the shortest distance
            spectrum = spectra[e_index]  # find the nearest spectrum
            # save 3 nearest spectra in the session
            nearest_spectra_ids_all.append([spectrum.id, spectra[distance.index(n_distance[2])].id, spectra[distance.index(n_distance[3])].id])
            if spectrum.nir_profile_id:
                s = NirProfile.objects.get(id=spectrum.nir_profile_id)
                if s:
                    messages.append(' belongs or is close to the group ' + s.title)
            else:
                messages.append(' is close to ' + spectrum.origin)
        self.request.session['nearest_spectra_ids_all'] = nearest_spectra_ids_all
        # print('debug: ',nearest_spectra_ids_all, len(nearest_spectra_ids_all))
        return messages

    def get_data(self):
        trans = self.cont['trans']
        return [[{"x":a,"y":b}] for a,b in trans[:,:2]]


class master_pca_element(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        data=super().get_context_data()
        data['app_label'] = 'masterModelling'
        data['model'] = 'StaticModel'
        data['index_text'] = 'master-pca-element'
        data['has_permission'] = self.request.user.is_authenticated
        data['verbose_name'] = 'MasterModellingPca'
        data['figure_header'] = 'Spectrum and its nearest spectra'
        data['master_pca_element'] = True
        id=self.request.GET.get('id','')
        self.request.session['id']=id
        return data

class master_pca_element_chart(BaseLineChartView):
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"})
        return default_opt

    def spec2context(self,**kwargs):
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        model=self.request.GET.get('model','')
        spectra=[]
        if model=='Match':
            id=self.request.GET.get('id','')
            spectrum = Match.objects.get(id=id)
            spectra_all = [i for i in Spectrum.objects.all()]
            spectra_all.insert(0, spectrum)
            y = normalize_y([i.y().tolist() for i in spectra_all])
            pca = PCA(n_components=2)
            pca.n_components_ = 2
            sm = StaticModel.objects.first()
            pca.components_ = sm.comp()
            pca.mean_ = np.mean(y, axis=0)
            trans = pca.transform(y)
            # print(trans)
            distances=[((trans[0][0]-i[0])**2+(trans[0][1]-i[1])**2)**0.5 for i in trans[1:]]
            # print('match distance:',distances)
            n_distances=sorted(distances)
            spectra=[spectra_all[distances.index(n_distances[i])+1] for i in [0,1,2]]
            spectra.insert(0,spectrum)
        else:
            id=int(self.request.session['id'])
            # print(id)
            spectrum=Spectrum.objects.all()[id]
            nearest_spectra_ids_all=self.request.session['nearest_spectra_ids_all']
            nearest_spectra_ids=nearest_spectra_ids_all[id]
            # print('nearest ids:',nearest_spectra_ids)
            spectra=[Spectrum.objects.get(id=i) for i in nearest_spectra_ids]
            spectra.insert(0,spectrum)
            # print(spectra)
        context.update({'spectra':spectra})
        return context

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


class master_pls(TemplateView):
    pass


class master_brix(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        data=super().get_context_data()
        data['app_label'] = 'masterModelling'
        data['model'] = 'IngredientModel'
        data['has_permission'] = self.request.user.is_authenticated
        data['verbose_name'] = 'Master_Brix'
        data['figure_header'] = 'Master modelling of ingredient Brix'
        data['master_brix'] = True
        return data

class master_brix_chart(BaseLineChartView):
    def get_context_data(self, **kwargs):
        content = {"labels": self.get_labels()}
        datasets = self.get_datasets()
        obj = datasets[len(datasets) - 1]
        obj['label'] = 'Latest uploaded spectrum: ' + obj['label']
        content.update({"datasets": datasets})
        context = self.cont
        context.update(content)
        return context

    def spec2context(self,**kwargs):
        context=super(BaseLineChartView, self).get_context_data(**kwargs)
        # select all spectra contain Brix
        nirprofile=NirProfile.objects.get(title='Grapes calibraition dataset - Alan Ames')
        spectra=[i for i in Spectrum.objects.filter(nir_profile_id=nirprofile.id)]
        # train pls model with Brix dataset
        X_train=normalize_y([i.y().tolist() for i in Spectrum.objects.all()])
        Y_train=np.array([float(re.findall('\d[\d\.]*', i.origin)[0]) for i in spectra])
        pls=PLSRegression(n_components=10)
        pls.fit(X_train,Y_train)
        Y_pred=pls.predict(Y_train)
        score=pls.score(Y_train)
        context.update({'Y_train':Y_train,'Y_pred':Y_pred,'score':score})
        return context


    def get_labels(self):
        pass

    def get_providers(self):
        pass

    def get_data(self):
        pass

