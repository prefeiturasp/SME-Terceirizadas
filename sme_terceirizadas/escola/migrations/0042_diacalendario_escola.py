# Generated by Django 2.2.13 on 2021-09-20 10:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0041_diacalendario'),
    ]

    operations = [
        migrations.AddField(
            model_name='diacalendario',
            name='escola',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='calendario', to='escola.Escola'),
        ),
    ]
