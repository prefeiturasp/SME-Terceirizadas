# Generated by Django 2.0.13 on 2019-08-09 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardapio', '0006_merge_20190805_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='suspensaoalimentacao',
            name='outro_motivo',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Outro motivo'),
        ),
        migrations.AddField(
            model_name='suspensaoalimentacao',
            name='prioritario',
            field=models.BooleanField(default=False),
        ),
    ]
