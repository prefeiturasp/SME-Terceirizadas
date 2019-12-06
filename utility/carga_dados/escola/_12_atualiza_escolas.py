import json
import os

import environ
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from sme_terceirizadas.escola.management.commands.helper import calcula_total_alunos_por_escola
from sme_terceirizadas.escola.models import (
    Escola)

ROOT_DIR = environ.Path(__file__) - 1
with open(os.path.join(ROOT_DIR, 'planilhas_de_carga', 'total_alunos.json'), 'r') as f:
    json_data = json.loads(f.read())


escola_totais = calcula_total_alunos_por_escola(json_data)

for codigo_eol, total in escola_totais.items():
    try:
        escola_object = Escola.objects.get(codigo_eol=codigo_eol)
        if escola_object.quantidade_alunos != total:
            print(f'Atualizando qtd alunos da escola {escola_object.nome} '
                  f'de {escola_object.quantidade_alunos} para {total}')

            escola_object.quantidade_alunos = total
            escola_object.save()
        else:
            print(f'Nada a ser feito em {escola_object.nome}')

    except ObjectDoesNotExist:
        print(f'Escola código EOL: {codigo_eol} não existe no banco ainda')
        continue
    except IntegrityError as e:
        print(f'Dados inconsistentes: {e}')
        continue
