# Generated by Django 3.2.20 on 2023-10-09 01:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kit_lanche", "0018_auto_20230921_1823"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaokitlancheunificada",
            name="evento",
            field=models.CharField(blank=True, max_length=160),
        ),
    ]
