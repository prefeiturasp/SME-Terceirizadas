# Generated by Django 2.2.13 on 2022-07-26 01:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0007_auto_20211008_1027"),
        ("produto", "0064_auto_20220630_0842"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="editais",
            field=models.ManyToManyField(
                blank=True, related_name="produtos", to="terceirizada.Edital"
            ),
        ),
    ]
