# Generated by Django 4.2.4 on 2023-08-25 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0023_alter_seats_seat_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='passenger',
            name='seat_type',
            field=models.CharField(choices=[('WINDOW', 'Window'), ('AISLE', 'Aisle'), ('MIDDLE', 'Middle')], default='WINDOW', max_length=15),
        ),
    ]