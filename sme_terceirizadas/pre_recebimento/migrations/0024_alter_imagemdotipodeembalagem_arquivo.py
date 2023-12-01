# Generated by Django 3.2.20 on 2023-10-03 15:54

import django.core.validators
from django.db import migrations, models

import sme_terceirizadas.dados_comuns.validators


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0023_alter_tipodeembalagemdelayout_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imagemdotipodeembalagem",
            name="arquivo",
            field=models.FileField(
                upload_to="layouts_de_embalagens",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["PDF", "PNG", "JPG", "JPEG"]
                    ),
                    sme_terceirizadas.dados_comuns.validators.validate_file_size_10mb,
                ],
            ),
        ),
    ]
