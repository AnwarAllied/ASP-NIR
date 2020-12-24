from django.forms import ModelForm
from myapp.models import NirProfile

# Create the form class.
# class NirProfileForm(ModelForm):
#     class Meta:
#         model = NirProfile
#         fields = ['pub_date', 'headline', 'content', 'reporter']

# Creating a form to add an article.
# form = ArticleForm()

# Creating a form to change an existing article.
# article = Article.objects.get(pk=1)
# form =NirProfileForm(instance=article)