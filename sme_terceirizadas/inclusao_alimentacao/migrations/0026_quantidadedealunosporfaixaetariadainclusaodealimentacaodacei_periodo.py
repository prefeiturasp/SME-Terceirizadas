# Generated by Django 2.2.13 on 2022-11-03 08:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0053_periodoescolar_tipo_turno'),
        ('inclusao_alimentacao', '0025_diasmotivosinclusaodealimentacaocemei_inclusaodealimentacaocemei_quantidadedealunosemeiinclusaodeali'),
    ]

    operations = [
        migrations.AddField(
            model_name='quantidadedealunosporfaixaetariadainclusaodealimentacaodacei',
            name='periodo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='escola.PeriodoEscolar'),
        ),
    ]
