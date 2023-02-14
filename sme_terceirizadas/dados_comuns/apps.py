from django.apps import AppConfig


class DadosComunsConfig(AppConfig):
    name = 'sme_terceirizadas.dados_comuns'

    def ready(self):
        import sme_terceirizadas.dados_comuns.signals  # noqa: F401
