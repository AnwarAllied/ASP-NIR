from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
import numpy as np
from django.shortcuts import reverse
from django.utils.html import format_html
from django_matplotlib import MatplotlibFigureField as ma
from django_resized import ResizedImageField
from django_dropbox_storage.storage import DropboxStorage
import dropbox

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


class Spectrum(models.Model):
    origin = models.CharField(max_length=60)
    code = models.CharField(max_length=60)
    color = models.CharField(max_length=60)
    y_axis = models.TextField()
    x_range_max = models.FloatField(blank=True, null=True)
    x_range_min = models.FloatField(blank=True, null=True)
    pic_path = models.CharField(max_length=300, blank=True, null=True)
    spec_pic = ResizedImageField(crop=['middle', 'center'], upload_to='nirpics',storage=DropboxStorage(),
                                 blank=True, null=True, verbose_name='Upload pic')
    nir_profile = models.ForeignKey(
        'NirProfile', on_delete=models.SET_NULL, blank=True, null=True)

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
        if self.spec_pic:
            return format_html('<img src="{}" style="width: 120px; height: 80px" />'.format(str(self.pic_path)))
        else:
            return format_html('<img src="{}" style="width: 120px; height: 80px" />'.format('/media/spectrum_default.png'))
    spec_image.short_description = 'Spec_pic'
        
    class Meta:
        verbose_name_plural = "Spectra"

# class SpectraDisplay(Spectrum):
#     class Meta:
#         proxy = True
#         verbose_name = 'Spectrum information'
#         verbose_name_plural = 'Spectra information'
#


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

    def __str__(self):
        return self.title

    def x(self,steps):
        return np.linspace(self.x_min, self.x_max, num=steps)

    def y(self,steps):
        return np.linspace(self.y_min, self.x_max, num=steps)

    def slug(self):
        return '_'.join(self.title.split())
