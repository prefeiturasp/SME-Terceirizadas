# Generated by Django 4.1.12 on 2023-10-26 10:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0016_alter_contrato_terceirizada"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contrato",
            name="numero",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="No do contrato"
            ),
        ),
    ]
