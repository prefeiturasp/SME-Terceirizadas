# Generated by Django 2.2.13 on 2022-07-29 04:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0067_produtoedital_ativo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produtoedital",
            name="tipo_produto",
            field=models.CharField(
                blank=True,
                choices=[("COMUM", "Comum"), ("DIETA_ESPECIAL", "Dieta especial")],
                max_length=25,
                null=True,
                verbose_name="tipo de produto",
            ),
        ),
    ]
