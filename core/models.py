from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
import numpy as np
from django.shortcuts import reverse
from django.utils.html import format_html
from django_matplotlib import MatplotlibFigureField as ma
from django_resized import ResizedImageField
try:
    from django_dropbox_storage.storage import DropboxStorage
except Exception as e:
    import traceback
    print('/'*20, 'Upgrade DropboxStorage to Python 3', '/'*20)
    t=traceback.format_exc()
    pa=t.split('File "')[1].split('", line')[0]
    print('Storage path:',pa)
    fi=open(pa,'r+')
    old=fi.read()
    fi.seek(0) # rewind
    new=old[:old.find('try')]+'try:\n    from io import StringIO ## for Python 3'+old[old.find('IO\n')+2:]
    new=new.replace('count.next()','next(count)')
    fi.write(new)
    print(new[:200], '...')
    fi.close()
    print('/'*20, 'Upgraded', '/'*20)
    from django_dropbox_storage.storage import DropboxStorage

SCRIPT_CHOICES = (
    ('A', 'Apout'),
    ('B', 'Blog'),
    ('I', 'Index'),
    ('G', 'Group'),
    ('S', 'Sup-group'),
    ('F', 'Featurs'),
    ('U', 'Sup-feature'),
)

REFERANCE_CHOICES = (
    ('A', 'Allied Scientific Pro'),
    ('L', 'Literature'),
    ('O', 'Other')
)

NIR_TYPE_CHOICES = (
    ('N', 'Not mentioned'),
    ('U', 'Unknown'),
    ('A', 'Type A'),
    ('B', 'Type B'),
)


# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
#     one_click_purchasing = models.BooleanField(default=False)

#     def __str__(self):
#         return self.user.username

class myStorage(DropboxStorage):
    def get_available_name(self, name, max_length=None):
        name = self._get_abs_path(name)
        if self.exists(name):
            self.delete(name)
        return name

class Spectrum(models.Model):
    origin = models.CharField(max_length=60)
    code = models.CharField(max_length=60)
    color = models.CharField(max_length=60)
    y_axis = models.TextField()
    x_range_max = models.FloatField(blank=True, null=True)
    x_range_min = models.FloatField(blank=True, null=True)
    pic_path = models.CharField(max_length=300, blank=True, null=True)
    spec_pic = ResizedImageField(crop=['middle', 'center'], upload_to='nirpics',storage=myStorage(),
                                 blank=True, null=True, verbose_name='Upload pic')
    nir_profile = models.ForeignKey(
        'NirProfile', on_delete=models.SET_NULL, blank=True, null=True)
    owner=models.ForeignKey(
        'Owner', on_delete=models.SET_NULL, blank=True, null=True, editable=False)

    def __str__(self):
        return self.origin

    def slug(self):
        return '_'.join(self.origin.split())

    def x(self):
        return np.linspace(int(self.x_range_min), int(self.x_range_max), num=np.shape(self.y())[0])

    def y(self):
        return np.array(eval("["+self.y_axis+"]"))

    def label(self):
        return self.origin

    def picpath(self):
        return self.pic_path

    def get_absolute_url(self):
        return reverse("core:spectrum", kwargs={
            'slug': self.slug()
        })

    def get_add_to_graph_url(self):
        return reverse("core:add-to-graph", kwargs={
            'slug': self.slug()
        })

    def get_remove_from_graph_url(self):
        return reverse("core:remove-from-graph", kwargs={
            'slug': self.slug()
        })

    def spec_image(self):
        if self.pic_path:
            return format_html('<img src="{}" style="width: 120px; height: 80px" />'.format(str(self.pic_path)))
        else:
            return format_html('<img src="{}" style="width: 120px; height: 80px" />'.format('/media/spectrum_default.png'))
    spec_image.short_description = 'Spec_pic'
        
    class Meta:
        verbose_name_plural = "Spectra"

class NirProfile(models.Model):
    title = models.CharField(max_length=100)

    nir_type = models.CharField(max_length=1, choices=NIR_TYPE_CHOICES, default="N")
    nir_method = models.TextField(blank=True, null=True)
    nir_configuration = models.TextField(blank=True, null=True)

    figure_id = models.CharField(max_length=10)
    figure_title = models.CharField(max_length=100)
    figure_caption = models.CharField(max_length=300)
    x_label = models.CharField(max_length=30)
    y_label = models.CharField(max_length=30)
    x_min = models.FloatField()
    x_max = models.FloatField()
    y_min = models.FloatField()
    y_max = models.FloatField()

    reference_type= models.CharField(max_length=1, choices=REFERANCE_CHOICES, default="A")
    reference_title = models.CharField(max_length=100)
    reference_link = models.CharField(max_length=100)
    owner=models.ForeignKey(
        'Owner', on_delete=models.SET_NULL, blank=True, null=True, editable=False)

    def __str__(self):
        return self.title

    def x(self,steps):
        return np.linspace(self.x_min, self.x_max, num=steps)

    def y(self,steps):
        return np.linspace(self.y_min, self.x_max, num=steps)

    def slug(self):
        return '_'.join(self.title.split())

class OwnerManager(models.Manager):
    def owner_obj(self,user,query):
        user_eml=user.email
        model_name = query.model._meta.model_name
        if not user_eml: # return only open obj if no email
            return self.get_open_obj(model_name)
        user_org=user_eml.split('@')[1].split('.')[0]
        return get_org_obj(model_name,user_org)
    
    def get_open_obj(self,model_name):
        op=super().get_queryset().get(orgnization='open')
        return eval("op."+model_name+"_set.all().order_by('id')")

    def get_org_obj(self,model_name,orgnization):
        obj, created=super().get_queryset().get_or_create(orgnization=orgnization)
        if created:
            obj.save()
        return eval("obj."+model_name+"_set.all().order_by('id')") #| self.get_open_obj(model_name)

    def get_id(self,user):
        user_eml=user.email
        if user_eml:
            user_org=user_eml.split('@')[1].split('.')[0]
            obj, created=super().get_queryset().get_or_create(orgnization=user_org)
            if created:
                obj.save()
            return obj.id
        else:
            return 1 # return open owner id

class Owner(models.Model):
    orgnization=models.CharField(max_length=100,default='open')
    o=OwnerManager()

    def __str__(self):
        return self.orgnization

    # u=User.objects.all()
    # e=[i.email.split('@')[1].split('.')[0] for i in u if i.email]