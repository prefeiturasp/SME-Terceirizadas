# Generated by Django 2.2.13 on 2022-08-04 10:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0052_auto_20220718_1810"),
        ("medicao_inicial", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="diasobremesadoce",
            unique_together={("tipo_unidade", "data")},
        ),
    ]
