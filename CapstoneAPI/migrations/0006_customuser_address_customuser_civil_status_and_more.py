# Generated by Django 5.1.5 on 2025-01-17 08:28

import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CapstoneAPI', '0005_alter_userprofile_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='customuser',
            name='civil_status',
            field=models.CharField(choices=[('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('widowed', 'Widowed'), ('in_a_civil_partnership', 'In a civil partnership')], default='single', max_length=100),
        ),
        migrations.AddField(
            model_name='customuser',
            name='middlename',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mobile',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region='PH'),
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
