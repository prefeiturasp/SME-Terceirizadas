# Generated by Django 3.2.18 on 2023-05-31 06:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('medicao_inicial', '0019_auto_20230531_0607'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anexoocorrenciamedicaoinicial',
            name='rastro_lote',
        ),
        migrations.RemoveField(
            model_name='anexoocorrenciamedicaoinicial',
            name='rastro_terceirizada',
        ),
        migrations.RemoveField(
            model_name='anexoocorrenciamedicaoinicial',
            name='status',
        ),
    ]