# import pytest
# from rest_framework.exceptions import ValidationError
#
# from ..api.validators import *
# # @pytest.mark.django_db
# # def test_valida_se_existe_o_cardapio(cardapio_valido):
# #     assert validators.cardapio_existe(cardapio_valido)
#
#
# @pytest.mark.django_db
# def test_valida_se_data_de_cardapio_eh_antiga(cardapio_valido, cardapio_invalido):
#     assert cardapio_antigo(cardapio_valido)
#     with pytest.raises(ValidationError, match='Não pode ser cardápio antigo'):
#         cardapio_antigo(cardapio_invalido)
#
# # @pytest.mark.django_db
# # def test_valida_se_data_de_cardapio_e_antiga(cardapio_valido, cardapio_invalido):
# #     assert cardapio_antigo(cardapio_valido)
# #     # assert not cardapio_antigo(cardapio_invalido.uuid)
#
# @pytest.mark.django_db
# def test_valida_se_as_datas_se_convergem(cardapio_valido, cardapio_valido2):
#     assert valida_cardapio_de_para(cardapio_valido, cardapio_valido2)
#     with pytest.raises(ValidationError, match='Data de cardápio para troca é superior a data de inversão'):
#         valida_cardapio_de_para(cardapio_valido2, cardapio_valido)
#
#
# @pytest.mark.django_db
# def test_valida_inexistencia_duplicidade(cardapio_valido, cardapio_valido2, escola):
#     assert valida_duplicidade(cardapio_valido, cardapio_valido2, escola)
