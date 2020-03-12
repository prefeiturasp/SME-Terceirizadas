#!/usr/bin/env bash
RED='\033[0;31m'
NC='\033[0m' # No Color
echo "Script de carga de dados... Sempre confira os dados para ver se está correto..."

echo "Ao final do script, deseja criar solicitações de teste? (S/N)"
read criar_solicitacoes

echo "Criar usuários para teste? (S/N)"
read criar_usuarios

echo "Associar admins à escola | dre | codae | terceirizada? VALIDO PARA DESENVOLVIMENTO / HOMOLOGAÇÃO (S/N)"
read associa_admins

./manage.py migrate
./manage.py loaddata sme_terceirizadas/**/fixtures/*.json

if [ "$criar_usuarios" != "${criar_usuarios#[Ss]}" ]; then
  echo "Criando usuários..."
  echo "Criando admin do sistema"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('admin@admin.com', 'adminadmin', cpf='11111111110', registro_funcional='1111110')"
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
fi

./manage.py shell -c "from utility.carga_dados.escola import _2_escola_EMEF_EMEFM_EMEBS_CIEJA"
./manage.py shell -c "from utility.carga_dados.escola import _3_escola_EMEI"
./manage.py shell -c "from utility.carga_dados.escola import _4_escola_CEI"
./manage.py shell -c "from utility.carga_dados.escola import _5_periodo_escolar"
./manage.py shell -c "from utility.carga_dados.escola import _6_periodo_escolar_tipo_alimentacao"

./manage.py shell -c "from utility.carga_dados.escola import _11_atualiza_dre"
./manage.py shell -c "from utility.carga_dados.escola import _12_atualiza_escolas"
./manage.py shell -c "from utility.carga_dados.dieta_especial import _13_dieta_especial"

echo -e "${RED}--------CRIANDO GESTORES DAS ESCOLAS----------${NC}"
./manage.py shell -c "from utility.carga_dados.escola import _7_diretor_escola"
echo -e "${RED}--------CRIANDO GESTORES DRE----------${NC}"
./manage.py shell -c "from utility.carga_dados.escola import _8_co_gestores_dre"
echo -e "${RED}--------CRIANDO GESTORES CODAE----------${NC}"
./manage.py shell -c "from utility.carga_dados.escola import _10_codae"

./manage.py shell -c "from utility.carga_dados.escola import _14_faixas_etarias"

echo -e "${RED}Criando cardápios... Devemos criar uma funcionalidade de criação de cardápipos. Esses aqui são TEMPORÁRIOS${NC}"

if [ "$criar_solicitacoes" != "${criar_solicitacoes#[Ss]}" ]; then
  echo "Criando solicitações..."
  ./manage.py shell -c "from utility.carga_dados._2_cardapio import _2_todas_as_solicitacoes"
  ./manage.py shell -c "from utility.carga_dados._2_cardapio import _3_solicitacoes_dieta_especial"
fi

if [ "$associa_admins" != "${associa_admins#[Ss]}" ]; then
  echo "Associado admins..."
  ./manage.py shell -c "from utility.carga_dados.escola import _9_associar_admins"
fi

./manage.py shell -c "from utility.carga_dados._2_cardapio import _1_cardapios"

./manage.py shell -c "from utility.carga_dados import email"
