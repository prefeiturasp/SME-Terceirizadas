# Generated by Django 4.2.7 on 2024-05-16 11:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0058_alter_cronograma_ficha_tecnica"),
    ]

    operations = [
        migrations.AddField(
            model_name="cronograma",
            name="observacoes",
            field=models.TextField(blank=True, verbose_name="Observações"),
        ),
    ]