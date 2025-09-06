from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    # return HttpResponse("Hello, this is the homepage!")
    return render(request, 'home.html')