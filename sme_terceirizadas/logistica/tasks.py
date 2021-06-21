import datetime

from config import celery
from django.template.loader import render_to_string

from ..dados_comuns.fluxo_status import GuiaRemessaWorkFlow
from ..dados_comuns.tasks import envia_email_em_massa_task
from ..logistica.models.guia import Guia


@celery.app.task(soft_time_limit=1000, time_limit=1200)
def avisa_a_escola_que_hoje_tem_entrega_de_alimentos():
    hoje = datetime.date.today()

    guias = Guia.objects.filter(status=GuiaRemessaWorkFlow.PENDENTE_DE_CONFERENCIA, data_entrega=hoje)

    for guia in guias.all():
        if guia.escola:
            email_query_set_escola = guia.escola.vinculos.filter(
                ativo=True
            ).values_list('usuario__email', flat=True)

            partes_interessadas = [email for email in email_query_set_escola]
        else:
            partes_interessadas = []

        html = render_to_string(
            template_name='logistica_avisa_ue_para_conferir_no_prazo.html',
            context={
                'titulo': 'Hoje tem entrega de alimentos',
            }
        )
        envia_email_em_massa_task.delay(
            assunto='[SIGPAE] Hoje tem entrega de alimentos',
            emails=partes_interessadas,
            corpo='',
            html=html
        )


@celery.app.task(soft_time_limit=1000, time_limit=1200)
def avisa_a_escola_que_tem_guias_pendestes_de_conferencia():
    hoje = datetime.date.today()

    guias = Guia.objects.filter(status=GuiaRemessaWorkFlow.PENDENTE_DE_CONFERENCIA, data_entrega__lt=hoje)

    for guia in guias.all():
        if guia.escola:
            email_query_set_escola = guia.escola.vinculos.filter(
                ativo=True
            ).values_list('usuario__email', flat=True)

            partes_interessadas = [email for email in email_query_set_escola]
        else:
            partes_interessadas = []

        html = render_to_string(
            template_name='logistica_avisa_ue_que_prazo_para_conferencia_foi_ultrapassado.html',
            context={
                'titulo': 'Registre a conferência da Guia de Remessa de alimentos!',
                'numero_guia': guia.numero_guia,
                'data_entrega': guia.data_entrega,
            }
        )
        envia_email_em_massa_task.delay(
            assunto='[SIGPAE] Registre a conferência da Guia de Remessa de alimentos!',
            emails=partes_interessadas,
            corpo='',
            html=html
        )
