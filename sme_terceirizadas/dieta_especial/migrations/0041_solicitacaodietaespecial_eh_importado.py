# Generated by Django 2.2.13 on 2021-10-27 19:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dieta_especial", "0040_auto_20211027_0152"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaodietaespecial",
            name="eh_importado",
            field=models.BooleanField(
                default=False, verbose_name="Proveniente de importacao?"
            ),
        ),
    ]
