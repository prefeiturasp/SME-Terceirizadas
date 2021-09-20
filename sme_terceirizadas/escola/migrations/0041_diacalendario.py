# Generated by Django 2.2.13 on 2021-09-17 18:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0040_auto_20210915_1641'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaCalendario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('data', models.DateField(verbose_name='Data')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('dia_letivo', models.BooleanField(default=True, verbose_name='É dia Letivo?')),
            ],
            options={
                'verbose_name': 'Dia',
                'verbose_name_plural': 'Dias',
                'ordering': ('data',),
            },
        ),
    ]
