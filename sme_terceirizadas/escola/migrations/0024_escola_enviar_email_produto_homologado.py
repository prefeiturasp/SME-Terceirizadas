# Generated by Django 2.2.13 on 2020-11-19 19:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0023_auto_20201009_1259"),
    ]

    operations = [
        migrations.AddField(
            model_name="escola",
            name="enviar_email_produto_homologado",
            field=models.BooleanField(
                default=False,
                help_text="Envia e-mail quando houver um produto com status de homologado, não homologado, ativar ou suspender.",
            ),
        ),
    ]
