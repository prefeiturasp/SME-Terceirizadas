#!/usr/bin/env bash
echo "Script de carga de dados para DESENVOLVIMENTO SOMENTE"

echo "Ao final do script, deseja criar solicitações de teste? (S/N)"
read criar_solicitacoes

./manage.py migrate

echo "Criando admin do sistema"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('admin@admin.com', 'adminadmin', cpf='11111111116', registro_funcional='1111116')"
echo "Criando Escola admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escola@admin.com', 'adminadmin', cpf='11111111111', registro_funcional='1111111')"
echo "Criando DRE admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('dre@admin.com', 'adminadmin', cpf='11111111112', registro_funcional='1111112')"
echo "Criando TERC admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('terceirizada@admin.com', 'adminadmin', cpf='11111111113', registro_funcional='1111113')"
echo "Criando CODAE admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('codae@admin.com', 'adminadmin', cpf='11111111114', registro_funcional='1111114')"
echo "Criando CODAE Nutricionista admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('nutricodae@admin.com', 'adminadmin', cpf='11111111115', registro_funcional='1111115')"
echo "Criando Escola CEI admin"
./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolacei@admin.com', 'adminadmin', cpf='11111111116', registro_funcional='1111116')"
./manage.py loaddata sme_terceirizadas/**/fixtures/*.json
./manage.py shell -c "from utility.carga_dados import run"

./manage.py shell -c "from utility.carga_dados.escola import _11_atualiza_dre"
./manage.py shell -c "from utility.carga_dados.escola import _12_atualiza_escolas"

./manage.py shell -c "from utility.carga_dados.dieta_especial import _13_dieta_especial"

./manage.py shell -c "from utility.carga_dados.escola import _8_co_gestores_dre"
./manage.py shell -c "from utility.carga_dados.escola import _10_codae"
./manage.py shell -c "from utility.carga_dados.escola import _9_associar_admins"
./manage.py shell -c "from utility.carga_dados.escola import _14_faixas_etarias"

if [ "$criar_solicitacoes" != "${criar_solicitacoes#[Ss]}" ] ;then
    echo "Criando solicitações..."
    ./manage.py shell -c "from utility.carga_dados._2_cardapio import _1_cardapios"
    ./manage.py shell -c "from utility.carga_dados._2_cardapio import _2_todas_as_solicitacoes"
    ./manage.py shell -c "from utility.carga_dados._2_cardapio import _3_solicitacoes_dieta_especial"
fi

