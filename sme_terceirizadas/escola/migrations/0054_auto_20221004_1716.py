# Generated by Django 2.2.13 on 2022-10-04 17:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0053_periodoescolar_tipo_turno"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planilhaatualizacaotipogestaoescola",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDENTE", "PENDENTE"),
                    ("SUCESSO", "SUCESSO"),
                    ("ERRO", "ERRO"),
                    ("PROCESSADO_COM_ERRO", "PROCESSADO_COM_ERRO"),
                    ("PROCESSANDO", "PROCESSANDO"),
                    ("REMOVIDO", "REMOVIDO"),
                ],
                default="PENDENTE",
                max_length=35,
                verbose_name="status",
            ),
        ),
    ]
