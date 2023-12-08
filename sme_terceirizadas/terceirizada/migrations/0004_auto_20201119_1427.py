# Generated by Django 2.2.13 on 2020-11-19 14:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0003_auto_20191213_1339"),
    ]

    operations = [
        migrations.AddField(
            model_name="terceirizada",
            name="bairro",
            field=models.CharField(blank=True, max_length=150, verbose_name="CEP"),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="cidade",
            field=models.CharField(blank=True, max_length=150, verbose_name="CEP"),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="complemento",
            field=models.CharField(blank=True, max_length=50, verbose_name="CEP"),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="eh_distribuidor",
            field=models.BooleanField(default=False, verbose_name="É distribuidor?"),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="estado",
            field=models.CharField(blank=True, max_length=150, verbose_name="CEP"),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="numero",
            field=models.CharField(blank=True, max_length=10, verbose_name="CEP"),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="responsavel_cargo",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="Representante cargo"
            ),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="responsavel_cpf",
            field=models.CharField(
                blank=True,
                max_length=11,
                null=True,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(11)],
            ),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="responsavel_email",
            field=models.CharField(
                blank=True, max_length=160, verbose_name="Responsável contato (email)"
            ),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="responsavel_nome",
            field=models.CharField(
                blank=True, max_length=160, verbose_name="Responsável"
            ),
        ),
        migrations.AddField(
            model_name="terceirizada",
            name="responsavel_telefone",
            field=models.CharField(
                blank=True,
                max_length=160,
                verbose_name="Representante contato (telefone)",
            ),
        ),
    ]
