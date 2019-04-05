#
# Loads school data from csv
#

import pandas as pd

from sme_pratoaberto_terceirizadas.school.models import School, ManagementType, SchoolUnitType, Borough
from sme_pratoaberto_terceirizadas.common_data.models import Address, CityLocation, Contact

df = pd.read_csv('escolas.csv', dtype={'CODAE': str}, sep=':')

# df['EOL']
df['UE'] = df['UE'].str.strip().str.upper()
df['NOME'] = df['NOME'].str.strip().str.upper()
df['DRE'] = df['DRE'].str.strip().str.upper()
df['DRE_SIGLA'] = df['DRE_SIGLA'].str.strip().str.upper()
df['LOTE'] = df['LOTE'].str.strip().str.upper()
df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
df['ENDERECO'] = df['ENDERECO'].str.strip().str.upper()
df['NUMERO'] = df['NUMERO'].str.strip().str.upper()
df['BAIRRO'] = df['BAIRRO'].str.strip().str.upper()
df['CEP'] = df['CEP'].str.strip()
df['TELEFONE1'] = df['TELEFONE1'].str.strip()
df['TELEFONE2'] = df['TELEFONE2'].str.strip()
df['EMPRESA'] = df['EMPRESA'].str.strip().str.upper()
# df['CODAE']


def check_create_borough(name, description):
    borough = Borough.objects.filter(name=name, is_active=True).first()
    if not borough:
        borough = Borough(name=name, description=description, is_active=True)
        borough.save()
    return borough.id


def check_create_management_type(name, description):
    mt = ManagementType.objects.filter(name=name, is_active=True).first()
    if not mt:
        mt = ManagementType(name=name, description=description, is_active=True)
        mt.save()
    return mt


def check_create_school_unit_type(name, description):
    ue = SchoolUnitType.objects.filter(name=name, is_active=True).first()
    if not ue:
        ue = SchoolUnitType(name=name, description=description, is_active=True)
        ue.save()
    return ue


def check_create_city_location(city, state):
    c_loc = CityLocation.objects.filter(city=city, state=state).first()
    if not c_loc:
        c_loc = CityLocation(city=city, state=state)
        c_loc.save()
    return c_loc


def create_address(line, city):
    # TODO common_data_address.complement pode ser NULL
    # TODO incluir complemento no csv
    # TODO common_data_address.lat e common_data_address.lon podem ser NULL
    addrss = Address(street_name=line.ENDERECO,
                      # complement=line.COMPLEMENTO,
                      district=line.BAIRRO,
                      number=line.NUMERO,
                      postal_code=line.CEP,
                      city_location=city)
    addrss.save()
    return addrss.id
# ----------------------------------------------------------------------------------------


for _, line in df.iterrows():
    print(line.NOME)

    # SUBPREFEITURA/BOROUGH
    # TODO Não tem subprefeitura no csv. Usando o nome da DRE.
    subpref = check_create_borough(line.DRE, 'Nome da DRE')

    # GESTÃO/MANAGEMENT_TYPE
    # TODO Sempre 'TERCEIRIZADA' ??
    gestao = check_create_management_type('TERCEIRIZADA', 'Gestão terceirizada')

    # UNIDADE ESCOLAR/SCHOOL UNIT
    ue = check_create_school_unit_type(line.UE, 'Unidade Escolar')

    # CIDADE-ESTADO/CITY-STATE
    # TODO por emquanto city='SÃO PAULO' state='SP'
    cidade = check_create_city_location('SÃO PAULO', 'SP')

    # ENDEREÇO/ADDRESS
    endereco = create_address(line, cidade)

    # ESCOLA/SCHOOL
    # TODO incluir agrupamento no csv. Assumindo 0.
    escola = School(name=line.NOME,
                    grouping = 0,
                    unit_type=ue,
                    management_type=gestao,
                    borough_id=subpref,
                    eol_code=line.EOL,
                    codae_code=line.CODAE,
                    is_active=True)
    escola.save()

    # CONTATO/CONTACT
    contato = Contact(name=line.NOME,
                      phone=line.TELEFONE1,
                      mobile_phone=line.TELEFONE2,
                      email=line.EMAIL)
    contato.save()
