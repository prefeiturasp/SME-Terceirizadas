import pytest
from faker import Faker
from model_mommy import mommy

from sme_pratoaberto_terceirizadas.meal_kit.models import MealKit
from sme_pratoaberto_terceirizadas.permission.models import Permission, ProfilePermission
from sme_pratoaberto_terceirizadas.users.models import Profile, Institution

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def meal_kit():
    #     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    #     name = models.CharField(_('Name'), max_length=160)
    #     description = models.TextField(_('Description'), blank=True, null=True)
    #     is_active = models.BooleanField(_('Is Active'), default=True)
    #     meals = models.ManyToManyField(Meal)
    return mommy.make(MealKit, name='kit lance nro tal', description='este kit lanche foi feito por fulano em...')


@pytest.fixture
def profile():
    institution = mommy.make(Institution, name='Faker SA')
    return mommy.make(Profile, title='título do perfil', institution=institution)


@pytest.fixture
def permission():
    return mommy.make(Permission, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')


@pytest.fixture
def profile_permission():
    permission = mommy.make(Permission, title='A permissão do fulano de tal', endpoint='http://meu.endpoint/')
    return mommy.make(ProfilePermission, permission=permission)
