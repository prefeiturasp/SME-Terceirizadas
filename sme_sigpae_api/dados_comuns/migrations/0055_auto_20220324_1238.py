# Generated by Django 2.2.13 on 2022-03-24 12:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0054_centraldedownload"),
    ]

    operations = [
        migrations.AlterField(
            model_name="centraldedownload",
            name="arquivo",
            field=models.FileField(
                blank=True, upload_to="cental_downloads", verbose_name="Arquivo"
            ),
        ),
    ]