# Generated by Django 2.2.13 on 2021-01-15 18:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0027_escola_codigo_codae"),
    ]

    operations = [
        migrations.AlterField(
            model_name="escola",
            name="codigo_codae",
            field=models.CharField(
                blank=True, default="", max_length=10, verbose_name="Código CODAE"
            ),
        ),
    ]
