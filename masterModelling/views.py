from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from .manages import update_master_model
import re
from .models import StaticModel,IngredientsModel
from core.models import Spectrum, NirProfile
from chartjs.views.lines import BaseLineChartView
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from predictionModel.models import normalize_y
from django.db.models import Q
import numpy as np
from spectraModelling.models import Match

class master_pca(TemplateView):
    template_name = 'admin/index_plot.html'

    def get_context_data(self, **kwargs):
        obj_id=int(self.request.GET.get('id',''))
        data = super().get_context_data()
        obj = StaticModel.objects.get(id=obj_id)
        text =eval(obj.profile)['titles']
        data['obj_id']=obj_id
        data['model'] = obj._meta.model_name
        data['master_static_pca'] = True
        data['has_permission'] = self.request.user.is_authenticated
        data['app_label'] = 'masterModelling'
        data['verbose_name'] = 'MasterModellingPca'
        data['figure_header']= 'Master model: '+obj.title
        data['text']=text
        data['spec_num']=obj.count
        data['group_num']=len(text)
        data['components']=obj.n_comp
        # data['score']=self.request.session['score']
        update=self.request.GET.get('update','')
        if update=='1':
            print(obj.title,'starts updating')
            success=update_master_model(obj_id)
            if success:
                messages.success(self.request, obj.title +' updated sucessfully' )
            else:
                messages.error(self.request, 'Opps! something went wrong')

        return data

class master_pca_chart(BaseLineChartView):
    def get_context_data(self, **kwargs):
        content = {"labels": self.get_labels()}
        datasets=self.get_datasets()
        
        # sort by profile color:
        
        color_ix={}
        colors, co_titles=self.cont['obj'].color()
        
        for i in range(len(colors)):
            datasets[i]['pointBackgroundColor']=colors[i]
            if colors[i] not in color_ix:
                color_ix.update({datasets[i]['pointBackgroundColor']:i})
        for i in color_ix.values():
            datasets[i]['label']=co_titles[i].capitalize()
        datasets[len(colors)-1]['pointBackgroundColor']=datasets[len(colors)-1]['pointBackgroundColor'][:-2]+'0.5)'
        content.update({"datasets": datasets,"color_ix":list(color_ix.values())+[len(colors)-1]})
        last_uploded=datasets[len(datasets)-1]
        
        if 'match_obj' in self.cont:
            last_uploded['label']='Unknown spectrum: close to '+ self.cont['msg'][-1]#last_uploded['label']
            # pass
        else:
            last_uploded['label']='Latest uploaded spectrum: close to '+last_uploded['label']
        
        # print(content['color_ix'])
        # print(datasets)
        context=self.cont
        context.update(content)
        return context

    def spec2context(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        model=self.request.GET.get('model','')
        obj_id=int(self.request.GET.get('id',''))
        obj = StaticModel.objects.get(id=obj_id)
        if model=='match':
            match_id=self.request.GET.get('match_id','')
            if not match_id:
                match_id=self.request.get_full_path().split('/')[2]
            
            match_obj=Match.objects.get(id=match_id)
            context.update({'match_obj':match_obj})
            obj=obj.add_match(match_obj)

        trans=obj.trans
        # print(np.array(eval(trans)).shape,obj.count, len(eval(obj.spectra)['ids']))
        context.update({'model':model,'obj': obj, 'trans':trans})
        return context

    def get_labels(self):
        self.cont = self.spec2context()
        return self.get_providers()

    def get_providers(self):
        messages=self.close_to()
        titles=eval(self.cont['obj'].spectra)['titles']
        return [i + j for i, j in zip(titles,messages)]

    def close_to(self):
        obj = self.cont['obj']
        spectra=eval(obj.spectra)
        profile=eval(obj.profile)
        obj_ids=spectra['ids']
        trans = np.array(eval(self.cont['trans']))
        messages = []
        distances=[[((i[0]-j[0])**2 + (i[1]-j[1])**2)**0.5 for i in trans] for j in trans]
        nearest_spectra_ids_all = []
        for distance in distances:
            n_distance=sorted(distance)  # sort
            e_index=distance.index(n_distance[1])  # [0] -> itself, find the index of the shortest distance
            nearest_spectra_ids_all.append([obj_ids[e_index], obj_ids[distance.index(n_distance[2])], obj_ids[distance.index(n_distance[3])]])
            if profile['ids'][e_index]:
                s = NirProfile.objects.get(id=profile['ids'][e_index])
                if s:
                    messages.append(s.title)
            else:
                messages.append(' is close to ' + spectra['titles'][e_index])
        # self.cont['nearest_spectra_ids_all'] = nearest_spectra_ids_all
        self.cont['msg']=messages
        # self.request.session['nearest_spectra_ids_all'] = nearest_spectra_ids_all
        # print('debug: ',nearest_spectra_ids_all[:6], len(nearest_spectra_ids_all), messages[-7:])
        return messages

    def get_data(self):
        trans = np.array(eval(self.cont['trans']))
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
            id=int(self.request.GET.get('id',''))
            spectrum = Match.objects.get(id=id)
            pca_method=self.request.GET.get('pca_method','')
            if pca_method == 'pca':
                sm=StaticModel.objects.filter(preprocessed='{}').first()
            elif pca_method == 'pca_kmScaled': 
                sm = StaticModel.objects.first()

            tran=sm.transform(spectrum.y())
            trans = np.array(eval(sm.trans))
            distances=[((tran[0][0]-i[0])**2+(tran[1][0]-i[1])**2)**0.5 for i in trans]
            # print('match distance:',distances)
            ids=eval(sm.spectra)['ids']
            n_distances=sorted(distances)
            ix=[distances.index(n_distances[i]) for i in [0,1,2]]
            spectra=[]
            for i in ix:
                try:
                    spectra.append(Spectrum.objects.get(id=ids[i]))
                except:
                    pass
            # spectra=Spectrum.objects.filter(eval('|'.join('Q(id='+str(pk)+')' for pk in ix)))
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