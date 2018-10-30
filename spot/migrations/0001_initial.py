# Generated by Django 2.1.2 on 2018-10-13 04:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song', models.TextField(blank=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spot.Album')),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spot.Artist')),
            ],
        ),
    ]