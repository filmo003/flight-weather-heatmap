from django.http import Http404
from django.shortcuts import render
from.models import Weather


def index(request):
    weather_list = Weather.objects.order_by('-platform_id')[:5]
    context = {
        'weather_list': weather_list,
    }
    return render(request, 'heatmap/index.html', context)


def detail(request, weather_id):
    try:
        weather = Weather.objects.get(pk=weather_id)
    except Weather.DoesNotExist:
        raise Http404("Weather does not exist")
    return render(request, 'heatmap/detail.html', {'weather': weather})