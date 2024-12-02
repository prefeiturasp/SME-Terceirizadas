from django.apps import AppConfig


class DadosComunsConfig(AppConfig):
    name = "sme_sigpae_api.dados_comuns"

    def ready(self):
        import sme_sigpae_api.dados_comuns.signals  # noqa: F401
