# Generated by Django 2.2.8 on 2020-04-26 19:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0014_auto_20200424_1627"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imagemdoproduto",
            name="arquivo",
            field=models.FileField(blank=True, null=True, upload_to=""),
        ),
        migrations.AlterField(
            model_name="imagemdoproduto",
            name="nome",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="produto",
            name="aditivos",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="produto",
            name="detalhes_da_dieta",
            field=models.TextField(blank=True, null=True),
        ),
    ]
