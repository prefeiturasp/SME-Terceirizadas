# Generated by Django 2.2.13 on 2023-01-20 17:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("kit_lanche", "0016_auto_20221125_1057"),
    ]

    operations = [
        migrations.AddField(
            model_name="escolaquantidade",
            name="cancelado",
            field=models.BooleanField(default=False, verbose_name="Esta cancelado?"),
        ),
        migrations.AddField(
            model_name="escolaquantidade",
            name="cancelado_em",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Cancelado em"
            ),
        ),
        migrations.AddField(
            model_name="escolaquantidade",
            name="cancelado_justificativa",
            field=models.CharField(
                blank=True,
                max_length=500,
                verbose_name="Porque foi cancelado individualmente",
            ),
        ),
        migrations.AddField(
            model_name="escolaquantidade",
            name="cancelado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
