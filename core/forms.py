from django import forms
from .models import NirProfile

# Create the form class.
class NirProfileForm(forms.ModelForm):
    adv = forms.CharField(max_length=60)
    class Meta:
        model = NirProfile
        fields = ['nir_type', 'nir_method', 'nir_configuration','figure_id', 'figure_title', 'figure_caption', 'x_label', 'y_label', 'x_min', 'x_max','y_min', 'y_max','reference_type', 'reference_title', 'reference_link']

# Creating a form to add an article.
# form = ArticleForm()

# Creating a form to change an existing article.
# article = Article.objects.get(pk=1)
# form =NirProfileForm(instance=article)