import csv
import os

import django  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")  # noqa
django.setup()

from sme_terceirizadas.escola.models import DiretoriaRegional, Escola, Lote, TipoGestao, TipoUnidadeEscolar  # noqa


def csv_to_list(filename: str) -> list:
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        csv_data = [line for line in reader]
    return csv_data


arquivo_escolas_novas = 'sme_terceirizadas/escola/data/escolas_novas_codigo_eol.csv'

escolas_novas = csv_to_list(arquivo_escolas_novas)


def cria_novas_escolas(unidade_escolar, codigo_eol, dre, nome_tipo_unidade, lote):
    tipo_gestao = TipoGestao.objects.get(nome='TERC TOTAL')
    tipo_unidade = TipoUnidadeEscolar.objects.filter(iniciais=nome_tipo_unidade).first()  # noqa
    Escola.objects.create(
        nome=unidade_escolar,
        codigo_eol=codigo_eol,
        diretoria_regional=dre,
        tipo_unidade=tipo_unidade,
        tipo_gestao=tipo_gestao,
        lote=lote
    )


def main():
    for item in escolas_novas:
        codigo_eol = str(item['CODIGO_EOL']).replace('.0', '').zfill(6)
        if Escola.objects.filter(codigo_eol=codigo_eol).first():
            continue
        if item['DRE'].strip() == 'CLI I' or item['DRE'].strip() == 'CLI II':
            item_dre = 'CL'
        else:
            item_dre = item['DRE'].strip()
        dre = DiretoriaRegional.objects.get(iniciais__icontains=item_dre)
        item_lote = item['DRE']
        lote = Lote.objects.get(iniciais=item_lote)
        cria_novas_escolas(item['UNIDADE_ESCOLAR'], codigo_eol, dre, item['TIPO'].strip(), lote)  # noqa

    print(Escola.objects.all().count(), 'escolas')  # noqa T001


if __name__ == '__main__':
    main()
