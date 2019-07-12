# Generated by Django 2.0.13 on 2019-07-10 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('escola', '0001_initial'),
        ('terceirizada', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='escola',
            name='lote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='terceirizada.Lote'),
        ),
        migrations.AddField(
            model_name='escola',
            name='periodos',
            field=models.ManyToManyField(blank=True, to='escola.PeriodoEscolar'),
        ),
        migrations.AddField(
            model_name='escola',
            name='tipo_gestao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='escola.TipoGestao'),
        ),
        migrations.AddField(
            model_name='escola',
            name='tipo_unidade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='escola.TipoUnidadeEscolar'),
        ),
    ]
