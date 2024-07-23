# Generated by Django 4.2.7 on 2024-06-17 11:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0054_merge_20240410_1440"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="controlesobras",
            name="data_hora_medicao",
        ),
        migrations.AddField(
            model_name="controlesobras",
            name="data_medicao",
            field=models.DateField(
                default=None, null=True, verbose_name="Data da medição"
            ),
        ),
        migrations.AddField(
            model_name="controlesobras",
            name="periodo",
            field=models.CharField(blank=True, max_length=1, verbose_name="Período"),
        ),
    ]