# Generated by Django 2.2.6 on 2019-11-20 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0003_auto_20191108_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='id',
        ),
        migrations.RemoveField(
            model_name='session',
            name='room',
        ),
        migrations.AlterField(
            model_name='session',
            name='purchase_link',
            field=models.CharField(max_length=256, primary_key=True, serialize=False),
        ),
    ]
