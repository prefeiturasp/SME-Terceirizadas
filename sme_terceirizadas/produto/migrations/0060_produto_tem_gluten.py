# Generated by Django 2.2.13 on 2021-09-27 11:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0059_auto_20210924_1832"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="tem_gluten",
            field=models.BooleanField(default=False, verbose_name="Tem Glúten?"),
        ),
    ]
