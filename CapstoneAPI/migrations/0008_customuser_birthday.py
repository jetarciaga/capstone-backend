# Generated by Django 5.1.1 on 2024-10-31 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CapstoneAPI', '0007_schedule_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
    ]