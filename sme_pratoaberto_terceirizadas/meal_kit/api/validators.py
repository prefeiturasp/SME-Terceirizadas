from django.contrib.auth.models import User
from sme_pratoaberto_terceirizadas.escola.models import Escola


def valida_usuario_escola(user: User):
    escola = Escola.objects.filter(users=user).first()
    if not escola:
        return False
    return True
