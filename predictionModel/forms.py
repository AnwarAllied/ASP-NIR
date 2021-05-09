from django import forms
# from .models import Poly
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = value.name.split('.')[-1]  # [0] returns path+filename
    valid_extensions = ['csv','xlsx', 'xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

# Create the form class.
class MatchForm(forms.Form):
    upload_a_spectrum_for_testing = forms.FileField(validators=[validate_file_extension], required=False)
    upload_a_spectrum_for_testing .widget.attrs.update({'accept':".csv"})


# Creating a form to add an article.
# form = ArticleForm()

# Creating a form to change an existing article.
# article = Article.objects.get(pk=1)
# form =NirProfileForm(instance=article)