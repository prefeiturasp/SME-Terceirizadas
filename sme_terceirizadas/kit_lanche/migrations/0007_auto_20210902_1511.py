# Generated by Django 2.2.13 on 2021-09-02 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('terceirizada', '0005_auto_20201127_1541'),
        ('kit_lanche', '0006_faixaetariasolicitacaokitlancheceiavulsa_solicitacaokitlancheceiavulsa'),
    ]

    operations = [
        migrations.AddField(
            model_name='kitlanche',
            name='descricao',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='kitlanche',
            name='edital',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='edital_kit_lanche', to='terceirizada.Edital'),
        ),
        migrations.AddField(
            model_name='kitlanche',
            name='status',
            field=models.CharField(choices=[('ATIVO', 'Ativo'), ('INATIVO', 'Inativo')], default='ATIVO', max_length=10),
        ),
    ]
