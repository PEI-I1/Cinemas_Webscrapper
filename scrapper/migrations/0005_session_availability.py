# Generated by Django 2.2.6 on 2019-11-20 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0004_auto_20191120_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='availability',
            field=models.IntegerField(default=0),
        ),
    ]
