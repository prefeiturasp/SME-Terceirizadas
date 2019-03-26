import pytest

from utility.common_functions import extract_digits
from .factories import OutSourceProfileFactory, AlternateProfileFactory, SubManagerProfileFactory, \
    RegionalDirectorProfileFactory, NutritionistProfileFactory

pytestmark = pytest.mark.django_db


def test_out_sourced_profile_model():
    """ Testando OutSourceProfile model """
    out_sourced = OutSourceProfileFactory.build(first_name='John',
                                                last_name='Jones',
                                                email='john@jones123.com',
                                                is_staff=False,
                                                cnpj='85.773.346/0001-85',
                                                state_registry='765420613384')
    assert out_sourced.get_short_name() == 'John'
    assert out_sourced.last_name == 'Jones'
    assert out_sourced.email == 'john@jones123.com'
    assert not out_sourced.is_staff
    assert out_sourced.cnpj == '85.773.346/0001-85'
    assert len(extract_digits(out_sourced.cnpj)) == 14
    assert extract_digits(out_sourced.cnpj) == '85773346000185'
    assert out_sourced.state_registry == '765420613384'


def test_alternate_profile_model():
    """ Testando AlternateProfile model """
    alternate = AlternateProfileFactory.build(first_name='John',
                                              last_name='Jones',
                                              email='john@jones123.com',
                                              username='john_jones',
                                              cpf='901.614.980-51')
    assert alternate.get_short_name() == 'John'
    assert alternate.last_name == 'Jones'
    assert alternate.get_full_name() == 'John Jones'
    assert alternate.get_username() == 'john_jones'
    assert alternate.email == 'john@jones123.com'
    assert alternate.cpf == '901.614.980-51'
    assert len(extract_digits(alternate.cpf)) == 11
    assert extract_digits(alternate.cpf) == '90161498051'


def test_sub_manager_profile_model():
    """ Testando SubManagerProfile model """
    sub_manager = SubManagerProfileFactory.build(first_name='Harrison',
                                                 last_name='Ford',
                                                 email='harrison@ford123.com',
                                                 username='harrison_ford')
    assert sub_manager.get_short_name() == 'Harrison'
    assert sub_manager.last_name == 'Ford'
    assert sub_manager.get_full_name() == 'Harrison Ford'
    assert sub_manager.get_username() == 'harrison_ford'
    assert sub_manager.email == 'harrison@ford123.com'


def test_regional_director_profile_model():
    """ Testando RegionalDirectorProfile model """
    alternate = AlternateProfileFactory.build()
    sub_manager = SubManagerProfileFactory.build()
    description = 'DRE responsible for Sé and Paraíso area'
    regional_director = RegionalDirectorProfileFactory.build(abbreviation='BT',
                                                             alternate=alternate,
                                                             description=description,
                                                             sub_manager=sub_manager)
    assert regional_director.abbreviation == 'BT'
    assert regional_director.alternate == alternate
    assert regional_director.description == 'DRE responsible for Sé and Paraíso area'
    assert regional_director.sub_manager == sub_manager


def test_nutritionist_profile_model():
    """ Testando NutritionistProfile model """
    regional_director = RegionalDirectorProfileFactory.build()
    nutritionist = NutritionistProfileFactory.build(regional_director=regional_director)
    assert nutritionist.regional_director == regional_director
