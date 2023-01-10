import datetime

import environ
from django.template.loader import render_to_string

from .tasks import envia_email_em_massa_task

env = environ.Env()
base_url = f'{env("REACT_APP_URL")}'


def _partes_interessadas_ue_cancela(obj):
    email_query_set_terceirizada = obj.escola.lote.terceirizada.emails_terceirizadas.filter(
        modulo__nome='Gestão de Alimentação'
    ).values_list('email', flat=True)
    return list(email_query_set_terceirizada)


def _preenche_template_e_envia_email_ue_cancela_parcialmente(obj, assunto, titulo, id_externo, criado_em,
                                                             partes_interessadas):
    url = f'{env("REACT_APP_URL")}/{obj.path}'
    template = 'fluxo_ue_cancela_parcialmente.html'
    dados_template = {'titulo': titulo, 'tipo_solicitacao': obj.DESCRICAO, 'id_externo': id_externo,
                      'criado_em': criado_em, 'nome_ue': obj.escola.nome, 'url': url,
                      'nome_dre': obj.escola.diretoria_regional.nome, 'nome_lote': obj.escola.lote.nome}
    html = render_to_string(template, dados_template)
    envia_email_em_massa_task.delay(
        assunto=assunto,
        corpo='',
        emails=partes_interessadas,
        template='fluxo_ue_cancela.html',
        dados_template=dados_template,
        html=html
    )


def ue_cancelar_pedido_parcialmente(obj):

    # envia email para partes interessadas
    id_externo = '#' + obj.id_externo
    assunto = '[SIGPAE] Status de solicitação - ' + id_externo
    titulo = f'Solicitação de {obj.tipo} Parcialmente Cancelada'
    momento_cancelamento = datetime.datetime.now()
    criado_em = momento_cancelamento.strftime('%d/%m/%Y - %H:%M')
    _preenche_template_e_envia_email_ue_cancela_parcialmente(obj, assunto, titulo, id_externo, criado_em,
                                                             _partes_interessadas_ue_cancela(obj))
