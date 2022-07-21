from django.contrib import admin

# Register your models here.
from .models import Weather

admin.site.register(Weather)
