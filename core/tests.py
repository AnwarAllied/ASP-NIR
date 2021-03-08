from django.test import TestCase
from django.test import Client
from django.contrib.admin.templatetags.admin_list import results, items_for_result
# Create your tests here.
# exec(open('core/tests.py','r').read())
c = Client()
response = c.post('/admin/login/', {'username': 'admin', 'password': 'password'})
response.status_code
response = c.get('/admin/core/spectrum/')
response.content

cl=response.context_data['cl']
res=list(results(cl))   # this is the results found in the changelist_results html.


