# Generated by Django 3.2.18 on 2023-09-19 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cardapio', '0048_controlerestos_imagemcontroleresto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagemcontroleresto',
            name='uuid',
        ),
    ]
