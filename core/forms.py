from django import forms
from .models import NirProfile, Spectrum
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = value.name.split('.')[-1]  # [0] returns path+filename
    valid_extensions = ['csv','xlsx', 'xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

# Create the form class.
class NirProfileForm(forms.ModelForm):
    upload_dataset = forms.FileField(validators=[validate_file_extension], required=False)
    upload_dataset.widget.attrs.update({'accept':".xls,.xlsx"})
    class Meta:
        model = NirProfile
        fields = ['nir_type', 'nir_method', 'nir_configuration','figure_id', 'figure_title', 'figure_caption', 'x_label', 'y_label', 'x_min', 'x_max','y_min', 'y_max','reference_type', 'reference_title', 'reference_link']

#form to display or add a spectrum
# class SpectrumForm(forms.Form):
#     upload_dataset = forms.ImageField()
#     upload_dataset.widget.attrs.update({'accept':'.jpg, .jpeg, .png'})
#     class Meta:
#         model = Spectrum
#         fields = ['origin', 'code', 'color', 'y_axis', 'x_range_max', 'x_range_min', 'pic_name', 'spec_pic', 'nir_profile']

# Creating a form to add an article.
# form = ArticleForm()

# Creating a form to change an existing article.
# article = Article.objects.get(pk=1)
# form =NirProfileForm(instance=article)