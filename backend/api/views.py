from django.shortcuts import render
from django.http import HttpResponse

def authorization(request):
    return render(request, 'index.html')


def about(requence):
    return HttpResponse("<h1>About API<h1>")