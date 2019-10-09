#!/usr/bin/env bash

echo "Script de carga de dados para DESENVOLVIMENTO SOMENTE"
./manage.py migrate

echo "Criando Escola admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escola@admin.com', 'adminadmin')"
echo "Criando DRE admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('dre@admin.com', 'adminadmin')"
echo "Criando TERC admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('terceirizada@admin.com', 'adminadmin')"
echo "Criando CODAE admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('codae@admin.com', 'adminadmin')"
./manage.py loaddata sme_terceirizadas/**/fixtures/*.json
./manage.py shell -c "from utility.carga_dados import run"
