# Generated by Django 2.2.13 on 2021-11-10 20:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inclusao_alimentacao", "0014_auto_20211110_2023"),
    ]

    operations = [
        migrations.AddField(
            model_name="inclusaoalimentacaonormal",
            name="terceirizada_conferiu_gestao",
            field=models.BooleanField(
                default=False, verbose_name="Terceirizada conferiu?"
            ),
        ),
    ]
