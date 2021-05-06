from django import forms
from django.core.exceptions import ValidationError

def pca_validate_file_extension(value):
    ext = value.name.split('.')[-1]  # [0] returns path+filename
    valid_extensions = ['csv','xlsx', 'xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

# Create the form class.
class PcaMatchForm(forms.ModelForm):
    select_a_spectrum = forms.FileField(validators=[pca_validate_file_extension], required=False)
    select_a_spectrum.widget.attrs.update({'accept':".csv"})