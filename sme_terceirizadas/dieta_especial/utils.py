from datetime import date

from django.template.loader import render_to_string
from rest_framework.pagination import PageNumberPagination

from sme_terceirizadas.perfil.models import Usuario
from sme_terceirizadas.relatorios.relatorios import relatorio_dieta_especial_conteudo
from sme_terceirizadas.relatorios.utils import html_to_pdf_email_anexo

from ..dados_comuns.constants import ADMINISTRADOR_TERCEIRIZADA, TIPO_SOLICITACAO_DIETA
from ..dados_comuns.fluxo_status import DietaEspecialWorkflow
from ..dados_comuns.utils import envia_email_unico, envia_email_unico_com_anexo_inmemory
from ..escola.models import Aluno
from ..paineis_consolidados.models import SolicitacoesCODAE
from .models import LogDietasAtivasCanceladasAutomaticamente, SolicitacaoDietaEspecial


def dietas_especiais_a_terminar():
    return SolicitacaoDietaEspecial.objects.filter(
        data_termino__lt=date.today(),
        ativo=True,
        status__in=[
            DietaEspecialWorkflow.CODAE_AUTORIZADO,
            DietaEspecialWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
            DietaEspecialWorkflow.ESCOLA_SOLICITOU_INATIVACAO
        ]
    )


def termina_dietas_especiais(usuario):
    for solicitacao in dietas_especiais_a_terminar():
        if solicitacao.tipo_solicitacao == TIPO_SOLICITACAO_DIETA.get('ALTERACAO_UE'):
            solicitacao.dieta_alterada.ativo = True
            solicitacao.dieta_alterada.save()
        solicitacao.termina(usuario)


def dietas_especiais_a_iniciar():
    return SolicitacaoDietaEspecial.objects.filter(
        data_inicio__lte=date.today(),
        tipo_solicitacao=TIPO_SOLICITACAO_DIETA.get('ALTERACAO_UE'),
        ativo=False,
        status__in=[
            DietaEspecialWorkflow.CODAE_AUTORIZADO,
            DietaEspecialWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
            DietaEspecialWorkflow.ESCOLA_SOLICITOU_INATIVACAO
        ]
    )


def inicia_dietas_temporarias(usuario):
    for solicitacao in dietas_especiais_a_iniciar():
        solicitacao.dieta_alterada.ativo = False
        solicitacao.dieta_alterada.save()


def aluno_pertence_a_escola_ou_esta_na_rede(cod_escola_no_eol, cod_escola_no_sigpae) -> bool:
    return cod_escola_no_eol == cod_escola_no_sigpae


def gerar_log_dietas_ativas_canceladas_automaticamente(dieta, dados, fora_da_rede=False):
    data = dict(
        dieta=dieta,
        codigo_eol_aluno=dados['codigo_eol_aluno'],
        nome_aluno=dados['nome_aluno'],
        codigo_eol_escola_destino=dados.get('codigo_eol_escola_origem'),
        nome_escola_destino=dados.get('nome_escola_origem'),
        codigo_eol_escola_origem=dados.get('codigo_eol_escola_destino'),
        nome_escola_origem=dados.get('nome_escola_destino'),
    )
    if fora_da_rede:
        data['codigo_eol_escola_origem'] = dados.get('codigo_eol_escola_origem')
        data['nome_escola_origem'] = dados.get('nome_escola_origem')
        data['codigo_eol_escola_destino'] = ''
        data['nome_escola_destino'] = ''
    LogDietasAtivasCanceladasAutomaticamente.objects.create(**data)


def _cancelar_dieta(dieta):
    usuario_admin = Usuario.objects.get(pk=1)
    dieta.cancelar_aluno_mudou_escola(user=usuario_admin)
    dieta.ativo = False
    dieta.save()


def _cancelar_dieta_aluno_fora_da_rede(dieta):
    usuario_admin = Usuario.objects.get(pk=1)
    dieta.cancelar_aluno_nao_pertence_rede(user=usuario_admin)
    dieta.ativo = False
    dieta.save()


def enviar_email_para_diretor_da_escola_origem(solicitacao_dieta, aluno, escola):  # noqa C901
    assunto = f'Cancelamento Automático de Dieta Especial Nº {solicitacao_dieta.id_externo}'
    hoje = date.today().strftime('%d/%m/%Y')
    template = 'email/email_dieta_cancelada_automaticamente_escola_origem.html',
    dados_template = {
        'nome_aluno': aluno.nome,
        'codigo_eol_aluno': aluno.codigo_eol,
        'dieta_numero': solicitacao_dieta.id_externo,
        'nome_escola': escola.nome,
        'hoje': hoje,
    }
    html = render_to_string(template, dados_template)
    terceirizada = escola.lote.terceirizada
    if terceirizada:
        emails = [contato.email for contato in terceirizada.contatos.all()]
        emails.append(escola.contato.email)
    else:
        emails = [escola.contato.email]

    for email in emails:
        envia_email_unico(
            assunto=assunto,
            corpo='',
            email=email,
            template=template,
            dados_template=dados_template,
            html=html,
        )


def enviar_email_para_escola_origem_eol(solicitacao_dieta, aluno, escola):
    assunto = 'Alerta para Criar uma Nova Dieta Especial'

    email_escola_origem_eol = escola.escola_destino.contato.email

    html_string = relatorio_dieta_especial_conteudo(solicitacao_dieta)
    anexo = html_to_pdf_email_anexo(html_string)
    anexo_nome = f'dieta_especial_{aluno.codigo_eol}.pdf'
    html_to_pdf_email_anexo(html_string)

    corpo = render_to_string(
        template_name='email/email_dieta_cancelada_automaticamente_escola_destino.html',
        context={
            'nome_aluno': aluno.nome,
            'codigo_eol_aluno': aluno.codigo_eol,
            'nome_escola': escola.nome,
        }
    )

    envia_email_unico_com_anexo_inmemory(
        assunto=assunto,
        corpo=corpo,
        email=email_escola_origem_eol,
        anexo_nome=anexo_nome,
        mimetypes='application/pdf',
        anexo=anexo,
    )


def enviar_email_para_escola_destino_eol(solicitacao_dieta, aluno, escola):
    assunto = 'Alerta para Criar uma Nova Dieta Especial'

    email_escola_destino_eol = escola.escola_destino.contato.email

    html_string = relatorio_dieta_especial_conteudo(solicitacao_dieta)
    anexo = html_to_pdf_email_anexo(html_string)
    anexo_nome = f'dieta_especial_{aluno.codigo_eol}.pdf'
    html_to_pdf_email_anexo(html_string)

    corpo = render_to_string(
        template_name='email/email_dieta_cancelada_automaticamente_escola_destino.html',
        context={
            'nome_aluno': aluno.nome,
            'codigo_eol_aluno': aluno.codigo_eol,
            'nome_escola': escola.nome,
        }
    )

    envia_email_unico_com_anexo_inmemory(
        assunto=assunto,
        corpo=corpo,
        email=email_escola_destino_eol,
        anexo_nome=anexo_nome,
        mimetypes='application/pdf',
        anexo=anexo,
    )


def enviar_email_para_diretor_da_escola_destino(solicitacao_dieta, aluno, escola):
    assunto = 'Alerta para Criar uma Nova Dieta Especial'
    email = escola.contato.email
    html_string = relatorio_dieta_especial_conteudo(solicitacao_dieta)
    anexo = html_to_pdf_email_anexo(html_string)
    anexo_nome = f'dieta_especial_{aluno.codigo_eol}.pdf'
    html_to_pdf_email_anexo(html_string)

    corpo = render_to_string(
        template_name='email/email_dieta_cancelada_automaticamente_escola_destino.html',
        context={
            'nome_aluno': aluno.nome,
            'codigo_eol_aluno': aluno.codigo_eol,
            'nome_escola': escola.nome,
        }
    )

    envia_email_unico_com_anexo_inmemory(
        assunto=assunto,
        corpo=corpo,
        email=email,
        anexo_nome=anexo_nome,
        mimetypes='application/pdf',
        anexo=anexo,
    )


def enviar_email_para_adm_terceirizada_da_escola_destino(solicitacao_dieta, aluno, escola, fora_da_rede=False):
    assunto = f'Cancelamento Automático de Dieta Especial Nº {solicitacao_dieta.id_externo}'
    hoje = date.today().strftime('%d/%m/%Y')
    template = 'email/email_dieta_cancelada_automaticamente_terceirizada_escola_destino.html',
    justificativa_cancelamento = 'por não pertencer a unidade educacional'
    if fora_da_rede:
        justificativa_cancelamento = 'por não estar matriculado'
    dados_template = {
        'nome_aluno': aluno.nome,
        'codigo_eol_aluno': aluno.codigo_eol,
        'dieta_numero': solicitacao_dieta.id_externo,
        'nome_escola': escola.nome,
        'hoje': hoje,
        'justificativa_cancelamento': justificativa_cancelamento,
    }
    html = render_to_string(template, dados_template)
    terceirizada = escola.lote.terceirizada
    if terceirizada:
        administradores_terceirizadas = [vinculo.usuario.email for vinculo in terceirizada.vinculos.filter(
            ativo=True,
            perfil__nome=ADMINISTRADOR_TERCEIRIZADA
        )]

        for email in administradores_terceirizadas:
            envia_email_unico(
                assunto=assunto,
                corpo='',
                email=email,
                template=template,
                dados_template=dados_template,
                html=html,
            )


def aluno_matriculado_em_outra_ue(aluno, solicitacao_dieta):
    if(aluno.escola):
        return aluno.escola.codigo_eol != solicitacao_dieta.escola.codigo_eol
    return False


def cancela_dietas_ativas_automaticamente():  # noqa C901 D205 D400
    dietas_ativas_comuns = SolicitacoesCODAE.get_autorizados_dieta_especial().filter(
        tipo_solicitacao_dieta='COMUM').order_by('pk').distinct('pk')
    for dieta in dietas_ativas_comuns:
        aluno = Aluno.objects.filter(codigo_eol=dieta.codigo_eol_aluno).first()
        solicitacao_dieta = SolicitacaoDietaEspecial.objects.filter(pk=dieta.pk).first()
        if aluno.nao_matriculado:
            dados = dict(
                codigo_eol_aluno=aluno.codigo_eol,
                nome_aluno=aluno.nome,
                codigo_eol_escola_origem=solicitacao_dieta.escola.codigo_eol,
                nome_escola_origem=solicitacao_dieta.escola.nome,
            )
            gerar_log_dietas_ativas_canceladas_automaticamente(solicitacao_dieta, dados, fora_da_rede=True)
            _cancelar_dieta_aluno_fora_da_rede(dieta=solicitacao_dieta)
            enviar_email_para_adm_terceirizada_da_escola_destino(
                solicitacao_dieta,
                aluno,
                escola=solicitacao_dieta.escola,
                fora_da_rede=True
            )
        elif aluno_matriculado_em_outra_ue(aluno, solicitacao_dieta):
            dados = dict(
                codigo_eol_aluno=aluno.codigo_eol,
                nome_aluno=aluno.nome,
                codigo_eol_escola_destino=aluno.escola.codigo_eol,
                nome_escola_destino=aluno.escola.nome,
                nome_escola_origem=solicitacao_dieta.escola.nome,
                codigo_eol_escola_origem=solicitacao_dieta.escola.codigo_eol,
            )
            gerar_log_dietas_ativas_canceladas_automaticamente(solicitacao_dieta, dados)
            _cancelar_dieta(solicitacao_dieta)
            enviar_email_para_adm_terceirizada_da_escola_destino(solicitacao_dieta, aluno, escola=aluno.escola)
        else:
            continue


class RelatorioPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProtocoloPadraoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def log_create(protocolo_padrao, user=None):
    import json
    from datetime import datetime

    historico = {}

    historico['created_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    historico['user'] = {'uuid': str(user.uuid), 'email': user.email} if user else user
    historico['action'] = 'CREATE'

    substituicoes = []
    for substituicao in protocolo_padrao.substituicoes.all():
        alimentos_substitutos = [
            {'uuid': str(sub.uuid), 'nome': sub.nome}
            for sub in substituicao.alimentos_substitutos.all()]
        subs = [
            {'uuid': str(sub.uuid), 'nome': sub.nome}
            for sub in substituicao.substitutos.all()]

        substitutos = [*alimentos_substitutos, *subs]
        substituicoes.append({
            'tipo': {'from': None, 'to': substituicao.tipo},
            'alimento': {'from': None, 'to': {'id': substituicao.alimento.id, 'nome': substituicao.alimento.nome}},
            'substitutos': {'from': None, 'to': substitutos}
        })

    historico['changes'] = [
        {'field': 'criado_em', 'from': None, 'to': protocolo_padrao.criado_em.strftime('%Y-%m-%d %H:%M:%S')},
        {'field': 'id', 'from': None, 'to': protocolo_padrao.id},
        {'field': 'nome_protocolo', 'from': None, 'to': protocolo_padrao.nome_protocolo},
        {'field': 'orientacoes_gerais', 'from': None, 'to': protocolo_padrao.orientacoes_gerais},
        {'field': 'status', 'from': None, 'to': protocolo_padrao.status},
        {'field': 'uuid', 'from': None, 'to': str(protocolo_padrao.uuid)},
        {'field': 'substituicoes', 'changes': substituicoes},
    ]

    protocolo_padrao.historico = json.dumps([historico])
    protocolo_padrao.save()


def log_update(instance, validated_data, substituicoes_old, substituicoes_new, user=None):
    import json
    from datetime import datetime
    historico = {}
    changes = diff_protocolo_padrao(instance, validated_data)
    changes_subs = diff_substituicoes(substituicoes_old, substituicoes_new)

    if changes_subs:
        changes.append({'field': 'substituicoes', 'changes': changes_subs})

    if changes:
        historico['updated_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        historico['user'] = {'uuid': str(user.uuid), 'email': user.email} if user else user
        historico['action'] = 'UPDATE'
        historico['changes'] = changes

        hist = json.loads(instance.historico) if instance.historico else []
        hist.append(historico)

        instance.historico = json.dumps(hist)


def diff_protocolo_padrao(instance, validated_data):
    changes = []

    if instance.nome_protocolo != validated_data['nome_protocolo']:
        changes.append(
            {'field': 'nome_protocolo', 'from': instance.nome_protocolo, 'to': validated_data['nome_protocolo']})

    if instance.orientacoes_gerais != validated_data['orientacoes_gerais']:
        changes.append(
            {
                'field': 'orientacoes_gerais',
                'from': instance.orientacoes_gerais,
                'to': validated_data['orientacoes_gerais']
            }
        )

    if instance.status != validated_data['status']:
        changes.append(
            {'field': 'status', 'from': instance.status, 'to': validated_data['status']})

    return changes


def diff_substituicoes(substituicoes_old, substituicoes_new): # noqa C901
    substituicoes = []

    # Tratando adição e edição de substituíções
    if substituicoes_old.all().count() <= len(substituicoes_new):

        for index, subs_new in enumerate(substituicoes_new):
            sub = {}

            try:
                subs = substituicoes_old.all().order_by('id')[index]
            except IndexError:
                subs = None

            if not subs or subs.alimento.id != subs_new['alimento'].id:
                sub['alimento'] = {
                    'from': {
                        'id': subs.alimento.id if subs else None,
                        'nome': subs.alimento.nome if subs else None},
                    'to': {
                        'id': subs_new['alimento'].id,
                        'nome': subs_new['alimento'].nome}}

            if not subs or subs.tipo != subs_new['tipo']:
                sub['tipo'] = {'from': subs.tipo if subs else None, 'to': subs_new['tipo'] if subs_new else None}

            al_subs_ids = subs.alimentos_substitutos.all().order_by('id').values_list('id', flat=True) if subs else []
            subs_ids_old = subs.substitutos.all().order_by('id').values_list('id', flat=True) if subs else []

            ids_olds = [*al_subs_ids, *subs_ids_old]
            ids_news = sorted([s.id for s in subs_new['substitutos']])

            from itertools import zip_longest
            if any(map(lambda t: t[0] != t[1], zip_longest(ids_olds, ids_news, fillvalue=False))):
                from_ = None

                if subs:
                    alimentos_substitutos = [
                        {'uuid': str(sub.uuid), 'nome': sub.nome}
                        for sub in subs.alimentos_substitutos.all()]

                    substitutos_ = [
                        {'uuid': str(sub.uuid), 'nome': sub.nome}
                        for sub in subs.substitutos.all()]

                    substitutos = [*alimentos_substitutos, *substitutos_]
                    from_ = [
                        {'uuid': sub['uuid'], 'nome': sub['nome']}
                        for sub in substitutos] if substitutos else None

                sub['substitutos'] = {
                    'from': from_,
                    'to': [
                        {'uuid': str(s.uuid), 'nome': s.nome}
                        for s in subs_new['substitutos']] if subs_new['substitutos'] else None
                }

            if sub:
                substituicoes.append(sub)

    else:
        # trata a remoção de uma substituíção
        for index, subs in enumerate(substituicoes_old.all()):
            sub = {}
            try:
                subs_new = substituicoes_new[index]
            except IndexError:
                subs_new = None

            if not subs_new or subs.alimento.id != subs_new['alimento'].id:
                sub['alimento'] = {
                    'from': {
                        'id': subs.alimento.id,
                        'nome': subs.alimento.nome
                    },
                    'to': {
                        'id': subs_new['alimento'].id if subs_new else None,
                        'nome': subs_new['alimento'].nome if subs_new else None
                    }
                }

            if not subs_new or subs.tipo != subs_new['tipo']:
                sub['tipo'] = {'from': subs.tipo, 'to': subs_new['tipo'] if subs_new else None}

            al_sub_ids = subs.alimentos_substitutos.all().order_by('id').values_list('id', flat=True) if subs else []
            subs_ids_old = subs.substitutos.all().order_by('id').values_list('id', flat=True) if subs else []

            ids_olds = [*al_sub_ids, *subs_ids_old]
            ids_news = sorted([s.id for s in subs_new['substitutos']]) if subs_new else []

            from itertools import zip_longest
            if any(map(lambda t: t[0] != t[1], zip_longest(ids_olds, ids_news, fillvalue=False))):
                to_ = None
                if subs_new:
                    to_ = [
                        {'uuid': str(s.uuid), 'nome': s.nome}
                        for s in subs_new['substitutos']] if subs_new['substitutos'] else None

                alimentos_substitutos = [
                    {'uuid': str(sub.uuid), 'nome': sub.nome}
                    for sub in subs.alimentos_substitutos.all()]

                substitutos_ = [
                    {'uuid': str(sub.uuid), 'nome': sub.nome}
                    for sub in subs.substitutos.all()]

                substitutos = [*alimentos_substitutos, *substitutos_]

                sub['substitutos'] = {
                    'from': [
                        {'uuid': sub['uuid'], 'nome': sub['nome']}
                        for sub in substitutos] if substitutos else None,
                    'to': to_
                }

            if sub:
                substituicoes.append(sub)

    return substituicoes
