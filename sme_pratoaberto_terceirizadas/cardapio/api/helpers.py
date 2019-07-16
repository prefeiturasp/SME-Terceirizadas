from sme_pratoaberto_terceirizadas.perfil.models import Usuario
from sme_pratoaberto_terceirizadas.utils import enviar_notificacao


# TODO Resolver conflitos de disparos de notificações
def notificar_partes_envolvidas(usuario: Usuario, **kwargs):
    # escola = kwargs['escola']
    # usuarios_dre = escola.diretoria_regional__usuarios
    # de = kwargs['cardapio_de']
    # para = kwargs['cardapio_para']
    # descricao = 'Solicitação para inversção de dia de cardápio da escola: {} do dia: {} para o dia {}'.format(
    #     escola.nome,
    #     de,
    #     para
    # )
    # enviar_notificacao(usuario, usuarios_dre, descricao, descricao)
    pass
