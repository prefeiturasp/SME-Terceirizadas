# Generated by Django 2.2.13 on 2022-07-18 05:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0050_periodoescolar_posicao"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="periodoescolar",
            options={
                "ordering": ("posicao",),
                "verbose_name": "Período escolar",
                "verbose_name_plural": "Períodos escolares",
            },
        ),
    ]
