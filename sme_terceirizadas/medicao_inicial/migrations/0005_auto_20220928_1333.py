# Generated by Django 2.2.13 on 2022-09-28 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medicao_inicial', '0004_categoriamedicao_medicao_valormedicao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anexoocorrenciamedicaoinicial',
            name='solicitacao_medicao_inicial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anexos', to='medicao_inicial.SolicitacaoMedicaoInicial'),
        ),
    ]
