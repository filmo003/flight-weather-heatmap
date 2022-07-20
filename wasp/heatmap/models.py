from django.db import models


# Create your models here.
class Weather(models.Model):
    platform_id = models.CharField(max_length=32, default='DEFAULT')
    base_text = models.CharField(max_length=512, default='DEFAULT')
    latitude = models.FloatField(default=999)
    longitude = models.FloatField(default=999)
    runway = models.IntegerField(default=999)
    year = models.IntegerField(default=999)
    month = models.IntegerField(default=999)
    day = models.IntegerField(default=999)
    hour = models.IntegerField(default=999)
    weather = models.CharField(max_length=512, default='weather')
    air_temp = models.FloatField(default=999)
    dew_point = models.FloatField(default=999)
    wind_direction = models.IntegerField(default=999)
    cross_wind = models.FloatField(default=999)
    wind_gust_speed = models.FloatField(default=999)
    peak_wind_speed = models.FloatField(default=999)
    precipitation = models.FloatField(default=999)
    visibility = models.IntegerField(default=999)
    cloud_cover = models.CharField(default='DEFAULT', max_length=64)
    cloud_ceiling = models.IntegerField(default=999)
    icing_percentage_low = models.FloatField(default=999)
    icing_percentage_med = models.FloatField(default=999)
    icing_percentage_high = models.FloatField(default=999)

    def __str__(self):
        return self.base_text