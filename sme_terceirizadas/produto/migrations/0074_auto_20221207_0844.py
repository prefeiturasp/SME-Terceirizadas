# Generated by Django 2.2.13 on 2022-12-07 08:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0073_auto_20220816_0216"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produtoedital",
            name="tipo_produto",
            field=models.CharField(
                choices=[("Comum", "Comum"), ("Dieta especial", "Dieta especial")],
                max_length=25,
                verbose_name="tipo de produto",
            ),
        ),
    ]
