from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# def index(request):
#     return HttpResponse("Hello, world. You're at the core index.")

def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('admin/index.html')
    context = {
        'whelcome': "Hello, world. You're at the core index.",
    }
    return HttpResponse(template.render(context, request))