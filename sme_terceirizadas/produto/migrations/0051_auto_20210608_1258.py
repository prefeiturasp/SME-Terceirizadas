# Generated by Django 2.2.13 on 2021-06-08 12:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0050_auto_20210607_1837"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reclamacaodeproduto",
            name="produto_lote",
            field=models.TextField(blank=True, default="", max_length=255),
        ),
    ]
