# Generated by Django 4.1.12 on 2023-10-10 18:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0015_auto_20230925_1221"),
        ("escola", "0062_diasuspensaoatividades"),
        ("inclusao_alimentacao", "0035_inclusaoalimentacaonormal_evento"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grupoinclusaoalimentacaonormal",
            name="rastro_dre",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_dre",
                to="escola.diretoriaregional",
            ),
        ),
        migrations.AlterField(
            model_name="grupoinclusaoalimentacaonormal",
            name="rastro_escola",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_escola",
                to="escola.escola",
            ),
        ),
        migrations.AlterField(
            model_name="grupoinclusaoalimentacaonormal",
            name="rastro_lote",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_lote",
                to="escola.lote",
            ),
        ),
        migrations.AlterField(
            model_name="grupoinclusaoalimentacaonormal",
            name="rastro_terceirizada",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_terceirizada",
                to="terceirizada.terceirizada",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaocontinua",
            name="rastro_dre",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_dre",
                to="escola.diretoriaregional",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaocontinua",
            name="rastro_escola",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_escola",
                to="escola.escola",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaocontinua",
            name="rastro_lote",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_lote",
                to="escola.lote",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaocontinua",
            name="rastro_terceirizada",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_terceirizada",
                to="terceirizada.terceirizada",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaodacei",
            name="rastro_dre",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_dre",
                to="escola.diretoriaregional",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaodacei",
            name="rastro_escola",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_escola",
                to="escola.escola",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaodacei",
            name="rastro_lote",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_lote",
                to="escola.lote",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaoalimentacaodacei",
            name="rastro_terceirizada",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_terceirizada",
                to="terceirizada.terceirizada",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaodealimentacaocemei",
            name="rastro_dre",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_dre",
                to="escola.diretoriaregional",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaodealimentacaocemei",
            name="rastro_escola",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_escola",
                to="escola.escola",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaodealimentacaocemei",
            name="rastro_lote",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_lote",
                to="escola.lote",
            ),
        ),
        migrations.AlterField(
            model_name="inclusaodealimentacaocemei",
            name="rastro_terceirizada",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="%(app_label)s_%(class)s_rastro_terceirizada",
                to="terceirizada.terceirizada",
            ),
        ),
    ]
