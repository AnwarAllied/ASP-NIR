from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django_matplotlib import MatplotlibFigureField as ma
import matplotlib.pyplot as plt
from django.core import serializers
import io, urllib, base64

# def index(request):
#     return HttpResponse("Hello, world. You're at the core index.")

def index(request):
    template = loader.get_template('admin/index.html')
    context = {
        'whelcome': "Hello, world. You're at the core index.",
    }
    return HttpResponse(template.render(context, request))

def plot(request):
    # print(dir(request),'\n',request.content_params)
    # print(request.get_full_path(),'\n',request.path)
    plt.plot(range(100))
    fig=plt.gcf()
    buf=io.BytesIO()
    fig.savefig(buf,format="png")
    buf.seek(0)
    string = base64.b64decode(buf.read())
    uri = urllib.parse.quote(string)
    return render(request,'admin/index1.html',{'data':uri})
    # fig=ma(figure='my_figure')
    # # return HttpResponse(str(dir(request))+str(request))
    # response = HttpResponse(content_type="application/json")
    # # print(dir(response),'\n',response.content)
    # serializers.serialize("json", fig, stream=response)
    # print(dir(response),'\n',response.content)
    # return response