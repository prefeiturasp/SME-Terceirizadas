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

echo "Atualizar dados com base na API do EOL em tempo real? (S/N)"
read atualizacao_tempo_real

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
  echo "Criando Nutricionista Supervisao admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('nutrisupervisao@admin.com', 'adminadmin', cpf='11111111125', registro_funcional='1111125')"
  echo "Criando CODAE - Gestao de Produtos - admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('gpcodae@admin.com', 'adminadmin', cpf='21111111114', registro_funcional='2111114')"
  echo "Criando Escola CEI admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolacei@admin.com', 'adminadmin', cpf='11111111116', registro_funcional='1111116')"
  echo "Criando Escola CEI CEU admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolaceiceu@admin.com', 'adminadmin', cpf='11111111117', registro_funcional='1111117')"
  echo "Criando Escola CCI admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolacci@admin.com', 'adminadmin', cpf='11111111118', registro_funcional='1111118')"
  echo "Criando Escola EMEF admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolaemef@admin.com', 'adminadmin', cpf='11111111119', registro_funcional='1111119')"
  echo "Criando Escola EMEBS admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolaemebs@admin.com', 'adminadmin', cpf='11111111120', registro_funcional='1111120')"
  echo "Criando Escola CIEJA admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolacieja@admin.com', 'adminadmin', cpf='11111111121', registro_funcional='1111121')"
  echo "Criando Escola EMEI admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolaemei@admin.com', 'adminadmin', cpf='11111111122', registro_funcional='1111122')"
  echo "Criando Escola CEU EMEI admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolaceuemei@admin.com', 'adminadmin', cpf='11111111123', registro_funcional='1111123')"
  echo "Criando Escola CEU EMEF admin"
  ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escolaceuemef@admin.com', 'adminadmin', cpf='11111111124', registro_funcional='1111124')"
fi

./manage.py shell -c "from utility.carga_dados.escola import _2_escola_EMEF_EMEFM_EMEBS_CIEJA"
./manage.py shell -c "from utility.carga_dados.escola import _3_escola_EMEI"
./manage.py shell -c "from utility.carga_dados.escola import _4_escola_CEI"
./manage.py shell -c "from utility.carga_dados.escola import _5_periodo_escolar"
./manage.py shell -c "from utility.carga_dados.escola import _6_periodo_escolar_tipo_alimentacao"

./manage.py shell -c "from utility.carga_dados.escola import _11_atualiza_dre"
./manage.py shell -c "from utility.carga_dados.escola import _12_atualiza_escolas"
./manage.py shell -c "from utility.carga_dados.dieta_especial import _13_dieta_especial"
./manage.py shell -c "from utility.carga_dados.dieta_especial import _16_dieta_especial_carga_alimentos"
# ./manage.py shell -c "from utility.carga_dados.produto import _1_carrega_diagnosticos"

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
  ./manage.py shell -c "from utility.carga_dados.cardapio import _2_todas_as_solicitacoes"
  ./manage.py shell -c "from utility.carga_dados.cardapio import _3_solicitacoes_dieta_especial"
fi

if [ "$associa_admins" != "${associa_admins#[Ss]}" ]; then
  echo "Associado admins..."
  ./manage.py shell -c "from utility.carga_dados.escola import _9_associar_admins"
fi

./manage.py shell -c "from utility.carga_dados.cardapio import _1_cardapios"

./manage.py shell -c "from utility.carga_dados import email"

if [ "$atualizacao_tempo_real" != "${atualizacao_tempo_real#[Ss]}" ]; then
  echo -e "${RED}Atualização com dados em tempo real da api do EOL${NC}"
  ./manage.py atualiza_dados_escolas
  ./manage.py atualiza_dres
  ./manage.py atualiza_total_alunos_escolas
fi

echo -e "${RED}Ativando/desativando dinamicamente o vínculo entre TipoUE e Períodos escolares${NC}"
./manage.py shell -c "from sme_terceirizadas.cardapio.tasks import ativa_desativa_vinculos_alimentacao_com_periodo_escolar_e_tipo_unidade_escolar; ativa_desativa_vinculos_alimentacao_com_periodo_escolar_e_tipo_unidade_escolar()"

./manage.py shell -c "from utility.carga_dados.escola import _15_cria_adms"
