# Generated by Django 4.2.7 on 2024-01-16 17:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0018_remove_contrato_pregao_chamada_publica_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contrato",
            name="ata",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="No da Ata"
            ),
        ),
    ]
