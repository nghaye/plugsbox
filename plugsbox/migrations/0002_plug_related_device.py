# Generated by Django 5.2.3 on 2025-07-01 09:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0207_remove_redundant_indexes'),
        ('plugsbox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plug',
            name='related_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_plugs', to='dcim.device'),
        ),
    ]
