# Generated by Django 4.2.7 on 2024-06-12 10:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "inclusao_alimentacao",
            "0037_diasmotivosinclusaodealimentacaocemei_descricao_evento",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="diasmotivosinclusaodealimentacaocei",
            name="cancelado_justificativa",
            field=models.CharField(
                blank=True,
                max_length=1500,
                verbose_name="Porque foi cancelado individualmente",
            ),
        ),
        migrations.AlterField(
            model_name="diasmotivosinclusaodealimentacaocemei",
            name="cancelado_justificativa",
            field=models.CharField(
                blank=True,
                max_length=1500,
                verbose_name="Porque foi cancelado individualmente",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaonormal",
            name="cancelado_justificativa",
            field=models.CharField(
                blank=True,
                max_length=1500,
                verbose_name="Porque foi cancelado individualmente",
            ),
        ),
        migrations.AlterField(
            model_name="quantidadeporperiodo",
            name="cancelado_justificativa",
            field=models.CharField(
                blank=True,
                max_length=1500,
                verbose_name="Porque foi cancelado individualmente",
            ),
        ),
    ]
