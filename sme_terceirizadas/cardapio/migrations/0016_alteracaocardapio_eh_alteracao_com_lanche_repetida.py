# Generated by Django 2.2.8 on 2020-04-01 19:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0015_suspensaoalimentacaodacei"),
    ]

    operations = [
        migrations.AddField(
            model_name="alteracaocardapio",
            name="eh_alteracao_com_lanche_repetida",
            field=models.BooleanField(default=False),
        ),
    ]
