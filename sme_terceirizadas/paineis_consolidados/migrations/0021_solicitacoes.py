import environ
from django.db import migrations

ROOT_DIR = environ.Path(__file__) - 2

sql_path = ROOT_DIR.path('sql', '0020_solicitacoes.sql')
with open(sql_path, 'r') as f:
    sql = f.read()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('paineis_consolidados', '0020_solicitacoes'),
        ('kit_lanche', '0013_auto_20220719_1755'),
        ('inclusao_alimentacao', '0024_auto_20220719_1755')
    ]

    operations = [
        migrations.RunSQL(sql),
    ]
