# Generated by Django 4.2.7 on 2024-07-02 21:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0032_alter_formulariosupervisao_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificacoesassinadasformulariobase",
            name="nome",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]