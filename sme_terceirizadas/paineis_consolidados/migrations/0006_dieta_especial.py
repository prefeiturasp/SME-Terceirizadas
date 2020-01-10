# Generated by Django 2.2.8 on 2020-01-06 19:29

import environ
from django.db import migrations

ROOT_DIR = environ.Path(__file__) - 2

sql_path = ROOT_DIR.path('sql', '0004_solicitacoes_dieta_especial.sql')
with open(sql_path, 'r') as f:
    sql = f.read()


class Migration(migrations.Migration):
    dependencies = [
        ('paineis_consolidados', '0005_delete_filtrosconsolidados'),
    ]

    operations = [
        migrations.RunSQL(sql),
    ]
