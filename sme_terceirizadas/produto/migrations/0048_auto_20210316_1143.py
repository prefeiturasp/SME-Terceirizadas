# Generated by Django 2.2.13 on 2021-03-16 11:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0047_auto_20210110_1811"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produto",
            name="componentes",
            field=models.CharField(
                blank=True, max_length=5000, verbose_name="Componentes do Produto"
            ),
        ),
    ]
