from sme_terceirizadas.perfil.models import Usuario
from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import progressbar


USUARIOS = [
    {
        'mensagem': 'admin do sistema',
        'email': 'admin@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111110',
        'registro_funcional': '1111110',
    },
    {
        'mensagem': 'Escola admin',
        'email': 'escola@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111111',
        'registro_funcional': '1111111',
    },
    {
        'mensagem': 'DRE admin',
        'email': 'dre@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111112',
        'registro_funcional': '1111112',
    },
    {
        'mensagem': 'TERC admin',
        'email': 'terceirizada@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111113',
        'registro_funcional': '1111113',
    },
    {
        'mensagem': 'CODAE admin',
        'email': 'codae@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111114',
        'registro_funcional': '1111114',
    },
    {
        'mensagem': 'CODAE Nutricionista admin',
        'email': 'nutricodae@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111115',
        'registro_funcional': '1111115',
    },
    {
        'mensagem': 'Nutricionista Supervisao admin',
        'email': 'nutrisupervisao@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111125',
        'registro_funcional': '1111125',
    },
    {
        'mensagem': 'CODAE - Gestao de Produtos - admin',
        'email': 'gpcodae@admin.com',
        'password': 'adminadmin',
        'cpf': '21111111114',
        'registro_funcional': '2111114',
    },
    {
        'mensagem': 'Escola CEI admin',
        'email': 'escolacei@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111116',
        'registro_funcional': '1111116',
    },
    {
        'mensagem': 'Escola CEI CEU admin',
        'email': 'escolaceiceu@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111117',
        'registro_funcional': '1111117',
    },
    {
        'mensagem': 'Escola CCI admin',
        'email': 'escolacci@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111118',
        'registro_funcional': '1111118',
    },
    {
        'mensagem': 'Escola EMEF admin',
        'email': 'escolaemef@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111119',
        'registro_funcional': '1111119',
    },
    {
        'mensagem': 'Escola EMEBS admin',
        'email': 'escolaemebs@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111120',
        'registro_funcional': '1111120',
    },
    {
        'mensagem': 'Escola CIEJA admin',
        'email': 'escolacieja@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111121',
        'registro_funcional': '1111121',
    },
    {
        'mensagem': 'Escola EMEI admin',
        'email': 'escolaemei@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111122',
        'registro_funcional': '1111122',
    },
    {
        'mensagem': 'Escola CEU EMEI admin',
        'email': 'escolaceuemei@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111123',
        'registro_funcional': '1111123',
    },
    {
        'mensagem': 'Escola CEU EMEF admin',
        'email': 'escolaceuemef@admin.com',
        'password': 'adminadmin',
        'cpf': '11111111124',
        'registro_funcional': '1111124',
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
            )
