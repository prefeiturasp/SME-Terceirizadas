# Generated by Django 4.1.12 on 2023-10-25 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sme_terceirizadas.dados_comuns.behaviors
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cardapio', '0045_alter_alteracaocardapio_rastro_dre_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataIntervaloAlteracaoCardapioCEMEI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('data', models.DateField(verbose_name='Data')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('cancelado', models.BooleanField(default=False, verbose_name='Esta cancelado?')),
                ('cancelado_justificativa', models.CharField(blank=True, max_length=500, verbose_name='Porque foi cancelado individualmente')),
                ('cancelado_em', models.DateTimeField(blank=True, null=True, verbose_name='Cancelado em')),
                ('alteracao_cardapio_cemei', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datas_intervalo', to='cardapio.alteracaocardapiocemei')),
                ('cancelado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Data do intervalo de Alteração de cardápio CEMEI',
                'verbose_name_plural': 'Datas do intervalo de Alteração de cardápio CEMEI',
                'ordering': ('data',),
            },
            bases=(models.Model, sme_terceirizadas.dados_comuns.behaviors.TemIdentificadorExternoAmigavel),
        ),
    ]
