# Generated by Django 4.2.7 on 2024-01-09 12:35

from django.db import migrations, models


def convert_to_float(apps, schema_editor):
    model = apps.get_model("pre_recebimento", "FichaTecnicaDoProduto")

    for obj in model.objects.all():
        try:
            obj.porcao_float = float(obj.porcao.replace(",", "."))
        except ValueError:
            obj.porcao_float = 0.0

        try:
            obj.valor_unidade_caseira_float = float(
                obj.valor_unidade_caseira.replace(",", ".")
            )
        except ValueError:
            obj.valor_unidade_caseira_float = 0.0

        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0039_alter_fichatecnicadoproduto_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="porcao_float",
            field=models.FloatField(blank=True, null=True, verbose_name="Porção"),
        ),
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="valor_unidade_caseira_float",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Unidade Caseira"
            ),
        ),
        migrations.RunPython(convert_to_float),
    ]
