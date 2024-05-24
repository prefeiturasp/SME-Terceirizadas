# Generated by Django 4.2.7 on 2024-05-16 17:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0025_alter_tipoocorrencia_managers"),
    ]

    operations = [
        migrations.AddField(
            model_name="formulariosupervisao",
            name="maior_frequencia_no_periodo",
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name="Maior Nº de Frequentes no Período"
            ),
        ),
    ]