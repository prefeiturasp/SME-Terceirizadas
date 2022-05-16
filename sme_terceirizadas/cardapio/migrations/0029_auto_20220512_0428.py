# Generated by Django 2.2.13 on 2022-05-12 04:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0045_auto_20220309_1632'),
        ('cardapio', '0028_motivodrenaovalida'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='horariodocombodotipodealimentacaoporunidadeescolar',
            name='combo_tipos_alimentacao',
        ),
        migrations.AddField(
            model_name='horariodocombodotipodealimentacaoporunidadeescolar',
            name='periodo_escolar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='escola.PeriodoEscolar'),
        ),
        migrations.AddField(
            model_name='horariodocombodotipodealimentacaoporunidadeescolar',
            name='tipo_alimentacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cardapio.TipoAlimentacao'),
        ),
    ]
