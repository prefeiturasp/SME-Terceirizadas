# Generated by Django 2.2.13 on 2020-11-23 11:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0024_escola_enviar_email_produto_homologado"),
    ]

    operations = [
        migrations.RenameField(
            model_name="escola",
            old_name="enviar_email_produto_homologado",
            new_name="enviar_email_por_produto",
        ),
    ]
