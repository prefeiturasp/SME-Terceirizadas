# Generated by Django 2.2.13 on 2021-10-08 15:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0061_especificacaoproduto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produto",
            name="tem_gluten",
            field=models.BooleanField(
                default=None, null=True, verbose_name="Tem Glúten?"
            ),
        ),
    ]