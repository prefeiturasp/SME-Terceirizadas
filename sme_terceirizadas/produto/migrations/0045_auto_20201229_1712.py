# Generated by Django 2.2.13 on 2020-12-29 17:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0044_nomedeprodutoedital"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="nomedeprodutoedital",
            unique_together={("nome",)},
        ),
    ]
