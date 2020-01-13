#!/usr/bin/env bash

echo "Script de carga de dados para DESENVOLVIMENTO SOMENTE"
./manage.py migrate

echo "Criando Escola admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escola@admin.com', 'adminadmin', cpf='11111111111', registro_funcional='1111111')"
echo "Criando DRE admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('dre@admin.com', 'adminadmin', cpf='11111111112', registro_funcional='1111112')"
echo "Criando TERC admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('terceirizada@admin.com', 'adminadmin', cpf='11111111113', registro_funcional='1111113')"
echo "Criando CODAE admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('codae@admin.com', 'adminadmin', cpf='11111111114', registro_funcional='1111114')"
echo "nutri"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('nutricodae@admin.com', 'adminadmin', cpf='11111111115', registro_funcional='1111115')"
./manage.py loaddata sme_terceirizadas/**/fixtures/*.json
./manage.py shell -c "from utility.carga_dados import run"

./manage.py shell -c "from utility.carga_dados.escola import _11_atualiza_dre"
./manage.py shell -c "from utility.carga_dados.escola import _12_atualiza_escolas"

./manage.py shell -c "from utility.carga_dados.escola import _8_co_gestores_dre"
./manage.py shell -c "from utility.carga_dados.escola import _10_codae"
./manage.py shell -c "from utility.carga_dados.escola import _9_associar_admins"

