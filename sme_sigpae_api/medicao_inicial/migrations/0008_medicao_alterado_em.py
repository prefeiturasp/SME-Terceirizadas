# Generated by Django 3.2.16 on 2023-02-09 18:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("medicao_inicial", "0007_auto_20230120_1706"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicao",
            name="alterado_em",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Alterado em"
            ),
        ),
    ]