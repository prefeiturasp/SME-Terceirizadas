# Generated by Django 2.2.13 on 2022-08-26 12:03

from django.db import migrations, models


def edital_default_78_2016(apps, _):
    ProtocoloPadraoDietaEspecial = apps.get_model(
        "dieta_especial", "ProtocoloPadraoDietaEspecial"
    )
    Edital = apps.get_model("terceirizada", "Edital")
    if Edital.objects.filter(numero__icontains="78/SME/2016").exists():
        edital = Edital.objects.get(numero__icontains="78/SME/2016")
        for protocolo in ProtocoloPadraoDietaEspecial.objects.all():
            protocolo.editais.add(edital)
            protocolo.save()


def backwards(apps, _):
    ProtocoloPadraoDietaEspecial = apps.get_model(
        "dieta_especial", "ProtocoloPadraoDietaEspecial"
    )
    Edital = apps.get_model("terceirizada", "Edital")
    if Edital.objects.filter(numero__icontains="78/SME/2016").exists():
        edital = Edital.objects.get(numero__icontains="78/SME/2016")
        for protocolo in ProtocoloPadraoDietaEspecial.objects.all():
            protocolo.editais.remove(edital)
            protocolo.save()


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0007_auto_20211008_1027"),
        ("dieta_especial", "0047_auto_20220321_0955"),
    ]

    operations = [
        migrations.AddField(
            model_name="protocolopadraodietaespecial",
            name="editais",
            field=models.ManyToManyField(
                related_name="protocolos_padroes_dieta_especial",
                to="terceirizada.Edital",
            ),
        ),
        migrations.RunPython(edital_default_78_2016, backwards),
    ]
