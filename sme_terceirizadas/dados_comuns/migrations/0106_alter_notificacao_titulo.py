# Generated by Django 4.1.12 on 2023-10-31 08:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0105_alter_logsolicitacoesusuario_status_evento"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificacao",
            name="titulo",
            field=models.CharField(
                blank=True, default="", max_length=200, verbose_name="Título"
            ),
        ),
    ]
