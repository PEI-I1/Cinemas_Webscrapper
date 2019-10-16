# Generated by Django 2.2.6 on 2019-10-16 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgeRating',
            fields=[
                ('age', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Cinema',
            fields=[
                ('coordinates', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('alt_name', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('city', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('original_title', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('title_pt', models.CharField(max_length=32)),
                ('producer', models.CharField(max_length=32)),
                ('cast', models.TextField()),
                ('synopsis', models.TextField()),
                ('length', models.IntegerField()),
                ('trailer_url', models.CharField(max_length=128)),
                ('banner_url', models.CharField(max_length=128)),
                ('released', models.BooleanField()),
                ('age_rating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrapper.AgeRating')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrapper.Genre')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('availability', models.IntegerField()),
                ('technology', models.CharField(max_length=32)),
                ('room', models.IntegerField()),
                ('purchase_link', models.CharField(max_length=256)),
                ('cinema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrapper.Cinema')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrapper.Movie')),
            ],
        ),
    ]