#-*- coding:utf-8 -*-
from django.http import HttpResponse

def dummy(request):
    """
    Dummy view that returns 200.
    Needed by nuxtjs : it calls /api/0.1/.
    """
    return HttpResponse("")
