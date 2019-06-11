from django.test import TestCase

from model_mommy import mommy


class SuspensaoDeAlimentacaoCase(TestCase):
    def setUp(self):
        self.status = mommy.make('StatusSuspensaoDeAlimentacao', _fill_optional=True)
        self.user = mommy.make('users.User', _fill_optional=True)
        self.suspensao = mommy.make('SuspensaoDeAlimentacao', _fill_optional=True, criado_por=self.user,
                                    status=self.status)

    def test_suspensao_de_alimentacao_str(self):
        self.assertEqual(self.suspensao.__str__(), self.status.nome + ' - ' + str(self.suspensao.id))
