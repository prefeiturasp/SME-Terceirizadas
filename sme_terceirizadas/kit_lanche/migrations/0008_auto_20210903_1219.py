# Generated by Django 2.2.13 on 2021-09-03 12:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kit_lanche", "0007_auto_20210902_1511"),
    ]

    operations = [
        migrations.AlterField(
            model_name="kitlanche",
            name="descricao",
            field=models.TextField(default=""),
        ),
    ]
