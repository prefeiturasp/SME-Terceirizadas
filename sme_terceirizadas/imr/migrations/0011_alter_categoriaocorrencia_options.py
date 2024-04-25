# Generated by Django 4.2.7 on 2024-04-25 11:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0010_importacaoplanilhatipoocorrencia"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="categoriaocorrencia",
            options={
                "ordering": ("posicao", "nome"),
                "verbose_name": "Categoria das Ocorrências",
                "verbose_name_plural": "Categorias das Ocorrências",
            },
        ),
    ]
