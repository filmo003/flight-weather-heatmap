# Generated by Django 4.0.1 on 2022-07-21 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heatmap', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='weather',
            old_name='precipitation',
            new_name='rain',
        ),
        migrations.RenameField(
            model_name='weather',
            old_name='platform_id',
            new_name='station_id',
        ),
        migrations.RemoveField(
            model_name='weather',
            name='cloud_cover',
        ),
        migrations.RemoveField(
            model_name='weather',
            name='runway',
        ),
        migrations.RemoveField(
            model_name='weather',
            name='weather',
        ),
        migrations.RemoveField(
            model_name='weather',
            name='wind_direction',
        ),
        migrations.AddField(
            model_name='weather',
            name='fog_haze',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='weather',
            name='freezing_rain',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='weather',
            name='hail',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='weather',
            name='snow',
            field=models.FloatField(default=999),
        ),
        migrations.AddField(
            model_name='weather',
            name='thunderstorms',
            field=models.BooleanField(default=0),
        ),
    ]