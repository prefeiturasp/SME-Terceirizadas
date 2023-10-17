# Generated by Django 4.1.12 on 2023-10-10 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('terceirizada', '0015_auto_20230925_1221'),
        ('escola', '0062_diasuspensaoatividades'),
        ('dieta_especial', '0056_logquantidadedietasautorizadas_periodo_escolar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaodietaespecial',
            name='rastro_dre',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(app_label)s_%(class)s_rastro_dre', to='escola.diretoriaregional'),
        ),
        migrations.AlterField(
            model_name='solicitacaodietaespecial',
            name='rastro_escola',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(app_label)s_%(class)s_rastro_escola', to='escola.escola'),
        ),
        migrations.AlterField(
            model_name='solicitacaodietaespecial',
            name='rastro_lote',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(app_label)s_%(class)s_rastro_lote', to='escola.lote'),
        ),
        migrations.AlterField(
            model_name='solicitacaodietaespecial',
            name='rastro_terceirizada',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(app_label)s_%(class)s_rastro_terceirizada', to='terceirizada.terceirizada'),
        ),
    ]
