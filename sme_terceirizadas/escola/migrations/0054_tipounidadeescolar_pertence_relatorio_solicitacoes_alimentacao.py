# Generated by Django 2.2.13 on 2022-11-21 11:49

from django.db import migrations, models


def pertence_relatorio_default(apps, _):
    TipoUnidadeEscolar = apps.get_model("escola", "TipoUnidadeEscolar")
    tipo_unidades_relatorio = [
        "CCI/CIPS",
        "CEI",
        "CEI CEU",
        "CEI DIRET",
        "CEMEI",
        "CEU CEI",
        "CEU CEMEI",
        "CEU EMEF",
        "CEU EMEI",
        "CEU GESTAO",
        "CIEJA",
        "EMEBS",
        "EMEF",
        "EMEFM",
        "EMEI",
    ]
    TipoUnidadeEscolar.objects.exclude(iniciais__in=tipo_unidades_relatorio).update(
        pertence_relatorio_solicitacoes_alimentacao=False
    )


def backwards(apps, _):
    TipoUnidadeEscolar = apps.get_model("escola", "TipoUnidadeEscolar")
    TipoUnidadeEscolar.objects.update(pertence_relatorio_solicitacoes_alimentacao=True)


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0053_periodoescolar_tipo_turno"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipounidadeescolar",
            name="pertence_relatorio_solicitacoes_alimentacao",
            field=models.BooleanField(
                default=True,
                help_text="Variável de controle para determinar quais tipos de unidade escolar são exibidos no "
                "relatório de solicitações de alimentação",
            ),
        ),
        migrations.RunPython(pertence_relatorio_default, backwards),
    ]
