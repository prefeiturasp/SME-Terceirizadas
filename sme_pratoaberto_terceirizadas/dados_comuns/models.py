from .models_abstract import Descritivel, CriadoEm, Nomeavel


class LogUsuario(Descritivel, CriadoEm):
    """Eventos de dados importantes para acompanhamento.
    Ex.: Fulano X a tarefa do tipo Z no dia tal, passando os dados W"""
    pass


class DiaSemana(Nomeavel):
    pass


class DiasUteis(object):
    def __init__(self, **kwargs):
        for campo in ('data_cinco_dias_uteis', 'data_dois_dias_uteis'):
            setattr(self, campo, kwargs.get(campo, None))
