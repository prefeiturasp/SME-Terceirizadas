# Generated by Django 2.2.13 on 2022-08-16 02:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0072_auto_20220804_1207"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="analisesensorial",
            name="homologacao_de_produto",
        ),
        migrations.RemoveField(
            model_name="reclamacaodeproduto",
            name="homologacao_de_produto",
        ),
        migrations.RemoveField(
            model_name="respostaanalisesensorial",
            name="homologacao_de_produto",
        ),
        migrations.DeleteModel(
            name="HomologacaoDoProduto",
        ),
    ]
