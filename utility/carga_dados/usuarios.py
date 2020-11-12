from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import progressbar

from sme_terceirizadas.perfil.models import Usuario

USUARIOS = [
    {
        'email': 'admin@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111100',
        'registro_funcional': '1111111',
        'nome': 'Admin',
        'cargo': 'Admin',
    },
    {
        'email': 'escola@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111101',
        'registro_funcional': '0000001',
        'nome': 'SUPER USUARIO ESCOLA',
        'cargo': 'Diretor',
    },
    {
        'email': 'dre@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111102',
        'registro_funcional': '0000010',
        'nome': 'SUPER USUARIO DRE',
        'cargo': 'Coordenador',
    },
    {
        'email': 'codae@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111103',
        'registro_funcional': '0000011',
        'nome': 'Gestão de Terceirizadas',
        'cargo': 'Coordenador',
    },
    {
        'email': 'gpcodae@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111104',
        'registro_funcional': '1000011',
        'nome': 'SUPER USUARIO GESTAO PRODUTO CODAE',
        'cargo': 'Nutricionista',
    },
    {
        'email': 'terceirizada@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111105',
        'registro_funcional': '0000100',
        'nome': 'SUPER USUARIO TERCEIRIZADA',
        'cargo': 'Gerente',
    },
    {
        'email': 'nutricodae@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111106',
        'registro_funcional': '0000101',
        'nome': 'SUPER USUARIO NUTRICIONISTA CODAE',
        'crn_numero': '15975364',
        'cargo': 'Nutricionista',
    },
    {
        'email': 'nutrisupervisao@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111107',
        'registro_funcional': '0010000',
        'nome': 'SUPER USUARIO NUTRICIONISTA SUPERVISAO',
        'crn_numero': '47135859',
        'cargo': 'Nutricionista',
    },
    {
        'email': 'escolacei@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111108',
        'registro_funcional': '0000110',
        'nome': 'SUPER USUARIO ESCOLA CEI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaceiceu@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111109',
        'registro_funcional': '0000111',
        'nome': 'SUPER USUARIO ESCOLA CEI CEU',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolacci@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111110',
        'registro_funcional': '0001000',
        'nome': 'SUPER USUARIO ESCOLA CCI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaemef@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111111',
        'registro_funcional': '0001001',
        'nome': 'SUPER USUARIO ESCOLA EMEF',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaemebs@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111112',
        'registro_funcional': '0001010',
        'nome': 'SUPER USUARIO ESCOLA EMEBS',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolacieja@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111113',
        'registro_funcional': '0001011',
        'nome': 'SUPER USUARIO ESCOLA CIEJA',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaemei@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111114',
        'registro_funcional': '0001100',
        'nome': 'SUPER USUARIO ESCOLA EMEI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaceuemei@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111115',
        'registro_funcional': '0001101',
        'nome': 'SUPER USUARIO ESCOLA CEU EMEI',
        'cargo': 'Diretor',
    },
    {
        'email': 'escolaceuemef@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111116',
        'registro_funcional': '0001111',
        'nome': 'SUPER USUARIO ESCOLA CEU EMEF',
        'cargo': 'Diretor',
    },
    {
        'email': 'dilog@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111117',
        'registro_funcional': '1110000',
        'nome': 'SUPER USUARIO DILOG',
        'cargo': 'Gerente',
    },
]


def cria_usuarios():
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
