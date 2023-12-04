# Generated by Django 2.2.13 on 2020-12-14 10:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0043_auto_20200827_1527"),
        ("dieta_especial", "0020_auto_20201130_1610"),
    ]

    operations = [
        migrations.AddField(
            model_name="alimento",
            name="ativo",
            field=models.BooleanField(default=True, verbose_name="Está ativo?"),
        ),
        migrations.AddField(
            model_name="alimento",
            name="marca",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="produto.Marca",
            ),
        ),
        migrations.AddField(
            model_name="alimento",
            name="outras_informacoes",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="alimento",
            name="tipo",
            field=models.CharField(
                choices=[("E", "Edital"), ("P", "Proprio")], default="E", max_length=1
            ),
        ),
        migrations.AlterUniqueTogether(
            name="alimento",
            unique_together={("nome", "marca")},
        ),
    ]
