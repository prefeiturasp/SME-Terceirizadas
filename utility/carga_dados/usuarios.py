from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import progressbar

from sme_terceirizadas.dados_comuns.constants import DJANGO_ADMIN_PASSWORD
from sme_terceirizadas.perfil.models import Usuario

USUARIOS = [
    {
        'email': 'admin@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111100',
        'registro_funcional': '1111111',
        'nome': 'Admin',
        'cargo': 'Admin',
    },
    {
        'email': 'escola@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111101',
        'registro_funcional': '0000001',
        'nome': 'SUPER USUARIO ESCOLA',
        'cargo': 'Diretor',
    },
    {
        'email': 'dre@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111102',
        'registro_funcional': '0000010',
        'nome': 'SUPER USUARIO DRE',
        'cargo': 'Coordenador',
    },
    {
        'email': 'codae@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111103',
        'registro_funcional': '0000011',
        'nome': 'Gestão de Terceirizadas',
        'cargo': 'Coordenador',
    },
    {
        'email': 'gpcodae@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111104',
        'registro_funcional': '1000011',
        'nome': 'SUPER USUARIO GESTAO PRODUTO CODAE',
        'cargo': 'Nutricionista',
    },
    {
        'email': 'terceirizada@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111105',
        'registro_funcional': '0000100',
        'nome': 'SUPER USUARIO TERCEIRIZADA',
        'cargo': 'Gerente',
    },
    {
        'email': 'nutricodae@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111106',
        'registro_funcional': '0000101',
        'nome': 'SUPER USUARIO NUTRICIONISTA CODAE',
        'crn_numero': '15975364',
        'cargo': 'Nutricionista',
    },
    {
        'email': 'nutrisupervisao@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111107',
        'registro_funcional': '0010000',
        'nome': 'SUPER USUARIO NUTRICIONISTA SUPERVISAO',
        'crn_numero': '47135859',
        'cargo': 'Nutricionista',
    },
    {
        'email': 'nutricionistamanifestacao@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '89237238002',
        'registro_funcional': '6348945',
        'nome': 'SUPER USUARIO NUTRICIONISTA MANIFESTACAO',
        'crn_numero': '47135859',
        'cargo': 'Nutricionista da Assessoria Jurídica',
    },
    {
        'email': 'escolacei@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111108',
        'registro_funcional': '0000110',
        'nome': 'SUPER USUARIO ESCOLA CEI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaceiceu@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111109',
        'registro_funcional': '0000111',
        'nome': 'SUPER USUARIO ESCOLA CEI CEU',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolacci@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111110',
        'registro_funcional': '0001000',
        'nome': 'SUPER USUARIO ESCOLA CCI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaemef@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111111',
        'registro_funcional': '0001001',
        'nome': 'SUPER USUARIO ESCOLA EMEF',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaemef3@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111133',
        'registro_funcional': '0001003',
        'nome': 'SUPER USUARIO ESCOLA EMEF',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaemebs@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111112',
        'registro_funcional': '0001010',
        'nome': 'SUPER USUARIO ESCOLA EMEBS',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolacieja@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111113',
        'registro_funcional': '0001011',
        'nome': 'SUPER USUARIO ESCOLA CIEJA',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaemei@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111114',
        'registro_funcional': '0001100',
        'nome': 'SUPER USUARIO ESCOLA EMEI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaceuemei@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111115',
        'registro_funcional': '0001101',
        'nome': 'SUPER USUARIO ESCOLA CEU EMEI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaceuemef@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111116',
        'registro_funcional': '0001111',
        'nome': 'SUPER USUARIO ESCOLA CEU EMEF',
        'cargo': 'Diretor',
    },
    {
        'email': 'papa@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111118',
        'registro_funcional': '0001112',
        'nome': 'SUPER USUARIO PAPA',
        'cargo': 'Diretor',
    },
    {
        'email': 'dilog@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111117',
        'registro_funcional': '1110000',
        'nome': 'SUPER USUARIO DILOG',
        'cargo': 'Gerente',
    },
    {
        'email': 'emefjoseermiriodemorais@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '',
        'registro_funcional': '',
        'nome': 'COORD EMEF JOSE ERMIRIO',
        'cargo': '',
    },
    {
        'email': 'ue@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111119',
        'registro_funcional': '1110001',
        'nome': 'SUPER USUARIO UE',
        'cargo': 'Gerente',
    },
    {
        'email': 'codaegabinete@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111120',
        'registro_funcional': '1230000',
        'nome': 'COORD CODAE GABINETE',
        'cargo': 'Gabinete',
    },
    {
        'email': 'codaelogistica@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111121',
        'registro_funcional': '1231000',
        'nome': 'COORD CODAE DILOG LOGISTICA',
        'cargo': 'Coordenador',
    },
    {
        'email': 'codaecontabil@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111122',
        'registro_funcional': '1232000',
        'nome': 'CODAE DILOG CONTABIL',
        'cargo': 'Contábil',
    },
    {
        'email': 'codaejuridico@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111123',
        'registro_funcional': '1233000',
        'nome': 'CODAE DILOG JURIDICO',
        'cargo': 'Jurídico',
    },
    {
        'email': 'uemista@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111124',
        'registro_funcional': '1235000',
        'nome': 'SUPER USUARIO UE MISTA',
        'cargo': 'Diretor',
    },
    {
        'email': 'uedireta@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111125',
        'registro_funcional': '1236000',
        'nome': 'SUPER USUARIO UE DIRETA',
        'cargo': 'Diretor',
    },
    {
        'email': 'ueparceira@admin.com',
        'password': DJANGO_ADMIN_PASSWORD,
        'cpf': '11111111126',
        'registro_funcional': '1237000',
        'nome': 'SUPER USUARIO UE PARCEIRA',
        'cargo': 'Diretor',
    },
]


def cria_usuarios(): # noqa C901
    for usuario in progressbar(USUARIOS, 'Usuario'):
        if Usuario.objects.filter(email=usuario['email']).first():
            print(f"{bcolors.FAIL}Usuário {usuario['email']} já existe!{bcolors.ENDC}")  # noqa
        else:
            Usuario.objects.create_superuser(
                email=usuario['email'],
                password=usuario['password'],
                cpf=usuario['cpf'],
                registro_funcional=usuario['registro_funcional'],
                nome=usuario['nome'],
                crn_numero=usuario.get('crn_numero'),
                cargo=usuario.get('cargo'),
            )

    try:
        user = Usuario.objects.get(email='papa@admin.com')
        Token.objects.get_or_create(user=user)
    except ObjectDoesNotExist:
        print(f"{bcolors.FAIL}Usuário papa@admin.com' não existe!{bcolors.ENDC}")  # noqa
