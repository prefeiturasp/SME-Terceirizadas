import os

from des.models import DynamicEmailConfiguration
from utility.carga_dados.escola.helper import bcolors

print(f'{bcolors.OKBLUE}Criando a configuração de email...')

DynamicEmailConfiguration.objects.create(
    host=os.environ['EMAIL_HOST'],
    port=os.environ['EMAIL_PORT'],
    from_email=os.environ['EMAIL_HOST_USER'],
    username=os.environ['EMAIL_HOST_USER'],
    password=os.environ['EMAIL_HOST_PASSWORD'],
    use_tls=os.environ['EMAIL_USE_TLS'],
    timeout=60
)
