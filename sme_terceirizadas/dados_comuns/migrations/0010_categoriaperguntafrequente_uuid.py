# Generated by Django 2.2.8 on 2020-04-24 14:15

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0009_categoriaperguntafrequente_perguntafrequente"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoriaperguntafrequente",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
