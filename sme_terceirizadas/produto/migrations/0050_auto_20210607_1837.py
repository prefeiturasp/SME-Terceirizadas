# Generated by Django 2.2.13 on 2021-06-07 18:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0049_auto_20210603_1657"),
    ]

    operations = [
        migrations.AddField(
            model_name="reclamacaodeproduto",
            name="produto_data_fabricacao",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="reclamacaodeproduto",
            name="produto_data_validade",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="reclamacaodeproduto",
            name="produto_lote",
            field=models.TextField(blank=True, max_length=255),
        ),
    ]
