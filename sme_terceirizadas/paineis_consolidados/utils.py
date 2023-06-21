import datetime
import unicodedata

from dateutil.relativedelta import relativedelta

from ..dados_comuns.utils import get_ultimo_dia_mes


def formata_resultado_inclusoes_etec_autorizadas(dia, mes, ano, inclusao):
    if (get_ultimo_dia_mes(datetime.date(int(ano), int(mes), 1)) < datetime.date.today() or
            dia < datetime.date.today().day):
        for qp in inclusao.quantidades_por_periodo.all():
            alimentacoes = ', '.join([
                unicodedata.normalize('NFD', alimentacao.nome.replace(' ', '_')).encode(
                    'ascii', 'ignore').decode('utf-8') for alimentacao in qp.tipos_alimentacao.all()]).lower()
            return {
                'dia': f'{dia:02d}',
                'periodo': f'{qp.periodo_escolar.nome}',
                'alimentacoes': alimentacoes,
                'numero_alunos': qp.numero_alunos,
                'inclusao_id_externo': inclusao.id_externo
            }


def tratar_dias_duplicados(return_dict):
    dict_tratado = []
    dias_tratados = []
    for obj in return_dict:
        dia = obj['dia']
        obj_dias_iguais = [r for r in return_dict if r['dia'] == dia]
        if obj['dia'] not in dias_tratados:
            if len(obj_dias_iguais) > 1:
                if any('lanche_emergencial' in obj['alimentacoes'] for obj in obj_dias_iguais):
                    numero_de_alunos = max(obj_dias_iguais, key=lambda obj: obj['numero_alunos'])['numero_alunos']
                    novo_objeto = {
                        'dia': dia,
                        'periodo': obj['periodo'],
                        'alimentacoes': ', '.join([obj['alimentacoes'] for obj in obj_dias_iguais]),
                        'numero_alunos': numero_de_alunos,
                        'inclusao_id_externo': None
                    }
                    dict_tratado.append(novo_objeto)
            else:
                dict_tratado.append(obj)
            dias_tratados.append(obj['dia'])
    return dict_tratado


def tratar_data_evento_final_no_mes(data_evento_final_no_mes, sol_escola, big_range):
    if sol_escola.data_evento_2.month != sol_escola.data_evento.month and not big_range:
        retorno = (sol_escola.data_evento + relativedelta(day=31)).day
    else:
        retorno = data_evento_final_no_mes
    return retorno


def get_dias_inclusao(obj, model_obj):
    if obj.tipo_doc == 'INC_ALIMENTA_CEI':
        return model_obj.dias_motivos_da_inclusao_cei.all()
    elif obj.tipo_doc == 'INC_ALIMENTA':
        return model_obj.inclusoes_normais.all()
    else:
        return model_obj.dias_motivos_da_inclusao_cemei.all()
