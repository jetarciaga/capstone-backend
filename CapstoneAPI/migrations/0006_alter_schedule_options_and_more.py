# Generated by Django 5.1.1 on 2024-10-05 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CapstoneAPI', '0005_alter_schedule_appointment_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='schedule',
            options={'ordering': ['date', 'timeslot']},
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='appointment_date',
            new_name='date',
        ),
        migrations.AddConstraint(
            model_name='schedule',
            constraint=models.UniqueConstraint(fields=('date', 'timeslot'), name='unique_schedule'),
        ),
    ]
