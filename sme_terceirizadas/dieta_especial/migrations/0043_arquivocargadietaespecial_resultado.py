# Generated by Django 2.2.13 on 2021-10-29 18:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dieta_especial", "0042_auto_20211028_1600"),
    ]

    operations = [
        migrations.AddField(
            model_name="arquivocargadietaespecial",
            name="resultado",
            field=models.FileField(blank=True, default="", upload_to=""),
        ),
    ]
