# Generated by Django 2.2.13 on 2021-10-19 10:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("kit_lanche", "0008_auto_20210903_1219"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="kitlanche",
            name="itens",
        ),
    ]
