# Generated by Django 2.2.8 on 2020-04-17 19:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0004_auto_20200416_2203"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imagemdoproduto",
            name="arquivo",
            field=models.FileField(blank=True, null=True, upload_to=""),
        ),
    ]
