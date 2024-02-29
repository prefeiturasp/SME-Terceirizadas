# Generated by Django 4.1.12 on 2023-10-23 15:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0062_diasuspensaoatividades"),
    ]

    operations = [
        migrations.AddField(
            model_name="aluno",
            name="ciclo",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="aluno",
            name="desc_ciclo",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="Descrição ciclo"
            ),
        ),
        migrations.AddField(
            model_name="aluno",
            name="desc_etapa",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="Descrição etapa"
            ),
        ),
        migrations.AddField(
            model_name="aluno",
            name="etapa",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
