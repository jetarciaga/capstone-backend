# Generated by Django 5.1.5 on 2025-01-16 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CapstoneAPI', '0003_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
