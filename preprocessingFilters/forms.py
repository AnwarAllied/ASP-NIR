from django import forms
from .models import SgFilter

# Create the form class.
class SgFilterForm(forms.ModelForm):
    class Meta:
        model = SgFilter
        fields = ['window_length', 'polyorder', 'deriv', 'mode', 'nirprofile'] 
        
# class SpectrumForm(forms.ModelForm):
#     class Meta:
#         model = Spectrum
#         exclude = ['pic_path']
# Creating a form to add an article.
# form = ArticleForm()

# Creating a form to change an existing article.
# article = Article.objects.get(pk=1)
# form =NirProfileForm(instance=article)