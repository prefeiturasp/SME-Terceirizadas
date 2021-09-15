# Generated by Django 2.2.13 on 2021-09-15 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0034_alunosmatriculadosperiodoescolaregular_logalunosmatriculadosperiodoescolaregular'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='logalunosmatriculadosperiodoescolaregular',
            options={'ordering': ('criado_em',), 'verbose_name': 'Log Alteração quantidade de alunos regular', 'verbose_name_plural': 'Logs de Alteração quantidade de alunos regulares'},
        ),
        migrations.AddField(
            model_name='alunosmatriculadosperiodoescolaregular',
            name='tipo_turma',
            field=models.CharField(blank=True, choices=[('REGULAR', 1), ('PROGRAMAS', 3)], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='logalunosmatriculadosperiodoescolaregular',
            name='tipo_turma',
            field=models.CharField(blank=True, choices=[('REGULAR', 1), ('PROGRAMAS', 3)], max_length=255, null=True),
        ),
    ]
