SME-Terceirizadas
=============================

.. image:: https://api.codeclimate.com/v1/badges/1f1cdb448bbc3f74efe3/maintainability
   :target: https://codeclimate.com/github/prefeiturasp/SME-PratoAberto-Terceirizadas/maintainability
   :alt: Maintainability
.. image:: https://api.codeclimate.com/v1/badges/1f1cdb448bbc3f74efe3/test_coverage
   :target: https://codeclimate.com/github/prefeiturasp/SME-PratoAberto-Terceirizadas/test_coverage
   :alt: Test Coverage
.. image:: https://travis-ci.org/prefeiturasp/SME-Terceirizadas.svg?branch=development
   :target: https://travis-ci.org/prefeiturasp/SME-Terceirizadas

Sistema de alimentação focado em terceirizadas


:License: GPLv3


Comandos Básicos
----------------

Carga inicial de dados
^^^^^^^^^^^^^^^^^^^^^^
* Rodar as migrations::

    $ ./manage.py migrate

* Criar os super usuários::

    $ ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('escola@admin.com', 'adminadmin')"
    $ ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('dre@admin.com', 'adminadmin')"
    $ ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('terceirizada@admin.com', 'adminadmin')"
    $ ./manage.py shell -c "from sme_terceirizadas.perfil.models import Usuario; Usuario.objects.create_superuser('codae@admin.com', 'adminadmin')"

* Carregar as fixtures::

    $ ./manage.py loaddata sme_terceirizadas/**/fixtures/*.json

* Carregar dados de planilhas excel junto com pedidos fake::

    $ ./manage.py shell -c "from utility.carga_dados import run"


* Ou rodar script de conveniência::

    $ ./utility/carga_de_dados.sh

Verificação de tipos de dados
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  $ mypy sme_pratoaberto_terceirizadas

Test coverage
^^^^^^^^^^^^^

Para executar testes em modo daemon, use o pytest-watch::

    $ ptw
