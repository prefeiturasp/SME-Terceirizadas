# Generated by Django 2.2.13 on 2021-10-07 18:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dieta_especial", "0036_protocolopadraodietaespecial_historico"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solicitacaodietaespecial",
            name="data_termino",
            field=models.DateField(null=True),
        ),
    ]
