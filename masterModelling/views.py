import json

import requests
from django.shortcuts import render
from django.views.generic import TemplateView
import re
from .models import StaticModel, IngredientsModel
from core.models import Spectrum, NirProfile
from chartjs.views.lines import BaseLineChartView
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from predictionModel.models import normalize_y, PcaModel
from django.db.models import Q
import numpy as np
from spectraModelling.models import Match
from chartjs.colors import next_color

class master_pca(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        obj,obj_id,text='','',''
        model=self.request.GET.get('model','')
        if model=='pred_pca':
            obj_id=int(self.request.GET.get('pca_id',''))
            pred_pca=PcaModel.objects.get(id=obj_id)
            obj=self.pred_pca2master_pca(pred_pca)
            obj.save()
            obj_id=obj.id
        else:
            obj_id = int(self.request.GET.get('id', ''))
            obj = StaticModel.objects.get(id=obj_id)
        if type(obj.profile) is dict:
            obj.profile=str(obj.profile)
        null=None
        # print(obj.profile,type(obj.profile))
        text = eval(obj.profile)['titles']
        data['figure_header'] = 'Master model: ' + obj.title
        data['spec_num'] = obj.count
        data['group_num'] = len(text)
        data['components'] = obj.n_comp
        data['obj_id'] = obj_id
        self.request.session['obj_id']=obj_id
        # data['model'] = obj._meta.model_name
        data['master_static_pca'] = True
        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = 'masterModelling'
        data['verbose_name'] = 'MasterModellingPca'
        data['text'] = text
        return data

    def pred_pca2master_pca(self,pred_pca):
        obj_id = int(self.request.GET.get('pca_id', ''))
        obj = PcaModel.objects.get(id=obj_id)
        pred_pca=obj
        pca_ids = self.request.session['pca_ids']
        title = pred_pca.__str__()
        spectra = []
        for i in pca_ids:
            spectra.append(Spectrum.objects.get(id=i))
        ids = [i.nir_profile_id for i in spectra]
        profile = json.dumps({'ids': ids, 'titles': [NirProfile.objects.get(id=i).title for i in set(ids) if i]})
        count=len(spectra)
        score=pred_pca.score
        n_comp=pred_pca.order
        trans='['+pred_pca.transform+']'
        preprocessed= json.dumps({})
        applied_model= json.dumps({'pca':title})
        master_pca=StaticModel()
        master_pca.title=title
        titles= [i.origin for i in spectra]
        colors, co_titles = obtain_colors(titles)
        master_pca.spectra= json.dumps({'ids':[i.id for i in spectra], 'titles':titles,'colors':colors,'color_titles':co_titles})
        master_pca.profile=profile
        master_pca.count=count
        master_pca.score=score
        master_pca.n_comp=n_comp
        master_pca.trans=trans
        master_pca.preprocessed=preprocessed
        master_pca.applied_model=applied_model
        return master_pca

def obtain_colors(titles):
    color_set = {'wheat': '255, 165, 0', 'durum': '235, 97, 35', 'narcotic': '120,120,120', 'tomato': '216, 31, 42',
                     'garlic': '128,128,128', 'grape': '0, 176, 24', 'other': '241 170 170'}
    # sp=kwargs['spectra']
    # s1=str(sp['titles']).lower()
    s1 = str(titles).lower()
    s2 = re.sub('[^\w ]+', '', s1)
    s3 = re.sub(r'\d+|\b\w{1,2}\b', '', s2)
    s4 = re.sub('brix|protein|moisture|data|test|validation|calibration|asp', '', s3)
    s5 = re.sub(' +', ' ', s4)
    s6 = re.findall('\w{3,}', s5)
    s7 = {s6.count(i): i for i in list(set(s6))}
    ls = sorted(s7.keys(), reverse=True)
    gp = []
    for i in eval(s1):
        has_origin = False
        for j in ls:
            if s7[j] in i and not has_origin:
                has_origin = True
                gp.append(s7[j])
        if not has_origin:
                gp.append('other')
    co = []
    ti = []
    ls = list(color_set.keys())
    for i in gp:
        has_origin = False
        for j in ls:
            if j in i and not has_origin:
                has_origin = True
                co.append('rgba(%s, 1)' % color_set[j])
                ti.append(j)
        if not has_origin:
            new_color = str(tuple(next(next_color())))
            co.append('rgba%s' % new_color)
            ti.append(i)
            ls.append(i)
            color_set.update({i: new_color[1:-1]})
    return co, ti


class master_pca_chart(BaseLineChartView):
    def get_context_data(self, **kwargs):
        content = {"labels": self.get_labels()}
        datasets = self.get_datasets()
        color_ix = {}
        colors, co_titles = self.cont['obj'].color()
        for i in range(len(colors)):
            datasets[i]['pointBackgroundColor'] = colors[i]
            if colors[i] not in color_ix:
                color_ix.update({datasets[i]['pointBackgroundColor']: i})
        for i in color_ix.values():
            datasets[i]['label'] = co_titles[i].capitalize()
        datasets[len(colors) - 1]['pointBackgroundColor'] = datasets[len(colors) - 1]['pointBackgroundColor'][
                                                            :-2] + '0.5)'
        content.update({"datasets": datasets, "color_ix": list(color_ix.values()) + [len(colors) - 1]})
        last_uploded = datasets[len(datasets) - 1]
        last_uploded['label'] = 'Latest uploaded spectrum: ' + last_uploded['label']

        # print(content['color_ix'])
        # print(datasets)
        context = self.cont
        context.update(content)
        return context

    def spec2context(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)

        obj_id = self.request.GET.get('id','')

        obj = StaticModel.objects.get(id=obj_id)

        trans = obj.trans
        context.update({'obj': obj, 'trans': trans})
        return context

    def get_labels(self):
        self.cont = self.spec2context()
        return self.get_providers()

    def get_providers(self):
        messages = self.close_to()
        titles = eval(self.cont['obj'].spectra)['titles']
        return [i + j for i, j in zip(titles, messages)]

    def close_to(self):
        obj = self.cont['obj']
        spectra = eval(obj.spectra)
        null=None
        profile = eval(obj.profile)
        obj_ids = spectra['ids']
        # print('ids:',obj_ids)
        trans = np.array(eval(self.cont['trans']))
        messages = []
        distances = [[((i[0] - j[0]) ** 2 + (i[1] - j[1]) ** 2) ** 0.5 for i in trans] for j in trans]
        nearest_spectra_ids_all = []
        for distance in distances:
            n_distance = sorted(distance)  # sort
            e_index = distance.index(n_distance[1])  # [0] -> itself, find the index of the shortest distance
            nearest_spectra_ids_all.append(
                [obj_ids[e_index], obj_ids[distance.index(n_distance[2])], obj_ids[distance.index(n_distance[3])]])
            if profile['ids'][e_index]:
                s = NirProfile.objects.get(id=profile['ids'][e_index])
                if s:
                    messages.append(s.title)
            else:
                messages.append(' is close to ' + spectra['titles'][e_index])
        self.request.session['nearest_spectra_ids_all'] = nearest_spectra_ids_all
        # print('debug: ',nearest_spectra_ids_all, len(nearest_spectra_ids_all))
        return messages

    def get_data(self):
        trans = np.array(eval(self.cont['trans']))
        return [[{"x": a, "y": b}] for a, b in trans[:, :2]]


class master_pca_element(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['app_label'] = 'masterModelling'
        data['model'] = 'StaticModel'
        data['index_text'] = 'master-pca-element'
        data['has_permission'] = self.request.user.is_authenticated
        data['verbose_name'] = 'MasterModellingPca'
        data['figure_header'] = 'Spectrum and its nearest spectra'
        data['master_pca_element'] = True
        id = self.request.GET.get('id', '')
        self.request.session['id'] = id
        return data


class master_pca_element_chart(BaseLineChartView):
    def get_dataset_options(self, index, color):
        default_opt = super().get_dataset_options(index, color)
        default_opt.update({"fill": "false"})
        return default_opt

    def spec2context(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        model = self.request.GET.get('model', '')
        spectra = []
        if model == 'Match':
            id = int(self.request.GET.get('id', ''))
            spectrum = Match.objects.get(id=id)
            pca_method = self.request.GET.get('pca_method', '')
            if pca_method == 'pca':
                sm = StaticModel.objects.filter(preprocessed='{}').first()
            elif pca_method == 'pca_kmScaled':
                sm = StaticModel.objects.first()

            tran = sm.transform(spectrum.y())
            trans = np.array(eval(sm.trans))
            distances = [((tran[0][0] - i[0]) ** 2 + (tran[1][0] - i[1]) ** 2) ** 0.5 for i in trans]
            # print('match distance:',distances)
            ids = eval(sm.spectra)['ids']
            n_distances = sorted(distances)
            ix = [distances.index(n_distances[i]) for i in [0, 1, 2]]
            spectra = []
            for i in ix:
                try:
                    spectra.append(Spectrum.objects.get(id=ids[i]))
                except:
                    pass
            # spectra=Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ix)))
            spectra.insert(0, spectrum)
        else:
            id = int(self.request.session['id'])
            # print(id)
            spectrum = Spectrum.objects.all()[id]
            nearest_spectra_ids_all = self.request.session['nearest_spectra_ids_all']
            nearest_spectra_ids = nearest_spectra_ids_all[id]
            # print('nearest ids:',nearest_spectra_ids)
            spectra = [Spectrum.objects.get(id=i) for i in nearest_spectra_ids]
            spectra.insert(0, spectrum)
            # print(spectra)
        context.update({'spectra': spectra})
        return context

    def get_labels(self):
        self.cont = self.spec2context()
        x = self.cont['spectra'][0].x()
        x = np.unique((np.round(x / 50) * 50).astype(int))
        self.cont['x_length'] = len(x)
        return x.tolist()

    def get_providers(self):
        return [i.label() for i in self.cont['spectra']]

    def get_data(self):
        x_length = self.cont['x_length']
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

