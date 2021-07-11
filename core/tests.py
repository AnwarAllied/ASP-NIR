from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from core.models import Spectrum, NirProfile, Owner
from spectraModelling.models import Match
from django.contrib.admin.templatetags.admin_list import results, items_for_result
# Create your tests here.
# exec(open('core/tests.py','r').read())
# c = Client()
# response = c.post('/admin/login/', {'username': 'admin', 'password': 'password'})
# response.status_code
# response = c.get('/admin/core/spectrum/')
# response.content


# cl=response.context_data['cl']
# qs = cl.queryset
# result=list(results(cl))   # this is the results found in the changelist_results html.
# it=[[i for i in r]+[q.spec_image()] for r,q in zip(result,qs.all())]

#
def ini_owner():
    o=Owner()
    o.save()
    u=User.objects.all()
    ua=User.objects.get(username='anwar')
    un=User.objects.get(username='user11')
    
    e=[i.email.split('@')[1].split('.')[0] for i in u if i.email]
    print("orgs:",set(e))
    for i in e:
        obj, created=Owner.o.get_or_create(orgnization=i.lower())
        if created:
            obj.save()
    asp_id=Owner.o.get_id(ua)
    nirva_id=Owner.o.get_id(un)
    for i in Spectrum.objects.all():
        if i.nir_profile:
            if i.nir_profile.id<16:
                i.owner_id=1
            else:
                i.owner_id=asp_id
        else:
            i.owner_id=asp_id
        i.save()
    for i in NirProfile.objects.all():
        if i.id<16:
            i.owner_id=1
        else:
            i.owner_id=asp_id
        i.save()
    for i in Match.objects.all():
        if i.id>80:
            i.owner_id=nirva_id
        else:
            i.owner_id=asp_id
        i.save()
    p=NirProfile.objects.get(id=20)
    p.owner_id=nirva_id
    p.save()
    for i in p.spectrum_set.all():
        i.owner_id=nirva_id
        i.save()