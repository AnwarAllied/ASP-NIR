from django.contrib import admin
from .models import Spectrum, NirProfile
from django.contrib.auth.models import Group ,User

class MyAdminSite(admin.AdminSite):
    default_site = 'myproject.admin.MyAdminSite'
    site_header = 'NIRvaScan - Allied Scientific Pro'
    site_title = 'NIR spectra'

admin.site.register(Spectrum)
admin.site.register(NirProfile)

admin_site = MyAdminSite(name='myadmin')
admin_site.register(Group)
admin_site.register(User)
admin_site.register(Spectrum)
admin_site.register(NirProfile)