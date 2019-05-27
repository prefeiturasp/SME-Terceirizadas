from django.contrib.auth.models import User
from sme_pratoaberto_terceirizadas.school.models import School


def valida_usuario_escola(user: User):
    escola = School.objects.filter(users=user).first()
    if not escola:
        return False
    return True
