# Generated by Django 4.2.7 on 2024-01-09 15:35

from django.db import migrations, models


def convert_to_float(apps, schema_editor):
    model = apps.get_model("pre_recebimento", "FichaTecnicaDoProduto")

    for obj in model.objects.all():
        try:
            obj.temperatura_congelamento_float = float(
                obj.temperatura_congelamento.replace(",", ".")
            )
        except ValueError:
            obj.temperatura_congelamento_float = 0.0

        try:
            obj.temperatura_veiculo_float = float(
                obj.temperatura_veiculo.replace(",", ".")
            )
        except ValueError:
            obj.temperatura_veiculo_float = 0.0

        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        (
            "pre_recebimento",
            "0042_rename_porcao_float_fichatecnicadoproduto_porcao_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="temperatura_congelamento_float",
            field=models.FloatField(
                blank=True,
                null=True,
                verbose_name="Temperatura de Congelamento do Produto",
            ),
        ),
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="temperatura_veiculo_float",
            field=models.FloatField(
                blank=True,
                null=True,
                verbose_name="Temperatura Interna do Veículo para Transporte",
            ),
        ),
        migrations.RunPython(convert_to_float),
        migrations.RemoveField(
            model_name="fichatecnicadoproduto",
            name="temperatura_congelamento",
        ),
        migrations.RemoveField(
            model_name="fichatecnicadoproduto",
            name="temperatura_veiculo",
        ),
        migrations.RenameField(
            model_name="fichatecnicadoproduto",
            old_name="temperatura_congelamento_float",
            new_name="temperatura_congelamento",
        ),
        migrations.RenameField(
            model_name="fichatecnicadoproduto",
            old_name="temperatura_veiculo_float",
            new_name="temperatura_veiculo",
        ),
    ]
