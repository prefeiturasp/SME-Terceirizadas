# Generated by Django 2.2.10 on 2020-06-18 19:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("perfil", "0008_auto_20191217_1146"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="cargo",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
