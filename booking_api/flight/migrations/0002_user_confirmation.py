# Generated by Django 4.2.4 on 2023-08-06 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirmation',
            field=models.CharField(default='test', max_length=128),
        ),
    ]