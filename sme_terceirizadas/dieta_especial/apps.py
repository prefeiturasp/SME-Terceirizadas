from django.apps import AppConfig


class DietaEspecialConfig(AppConfig):
    name = 'sme_terceirizadas.dieta_especial'

    def ready(self):
        import sme_terceirizadas.dieta_especial.signals  # noqa: F401
