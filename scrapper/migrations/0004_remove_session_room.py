# Generated by Django 2.2.6 on 2019-11-09 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0003_auto_20191108_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='room',
        ),
    ]
