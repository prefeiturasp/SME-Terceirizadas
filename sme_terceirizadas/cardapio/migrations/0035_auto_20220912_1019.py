# Generated by Django 2.2.13 on 2022-09-12 10:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0034_inversaocardapio_alunos_da_cemei"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inversaocardapio",
            name="alunos_da_cemei",
            field=models.CharField(
                blank=True, default="", max_length=50, verbose_name="Alunos da CEMEI"
            ),
        ),
    ]
