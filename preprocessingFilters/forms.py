from django import forms
from .models import SgFilter

# Create the form class.
class SgFilterForm(forms.ModelForm):
    class Meta:
        model = SgFilter
        fields = ['window_length', 'polyorder', 'deriv', 'mode', 'nirprofile']