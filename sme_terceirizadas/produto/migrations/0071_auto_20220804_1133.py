# Generated by Django 2.2.13 on 2022-08-04 11:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0007_auto_20211008_1027"),
        ("produto", "0070_auto_20220803_0134"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="produtoedital",
            unique_together={("produto", "edital")},
        ),
    ]
