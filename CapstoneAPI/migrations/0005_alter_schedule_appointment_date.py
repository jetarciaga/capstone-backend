# Generated by Django 5.1.1 on 2024-10-03 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CapstoneAPI', '0004_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='appointment_date',
            field=models.DateField(),
        ),
    ]