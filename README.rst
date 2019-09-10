SME-Terceirizadas
=============================

.. image:: https://api.codeclimate.com/v1/badges/1f1cdb448bbc3f74efe3/maintainability
   :target: https://codeclimate.com/github/prefeiturasp/SME-PratoAberto-Terceirizadas/maintainability
   :alt: Maintainability
.. image:: https://api.codeclimate.com/v1/badges/1f1cdb448bbc3f74efe3/test_coverage
   :target: https://codeclimate.com/github/prefeiturasp/SME-PratoAberto-Terceirizadas/test_coverage
   :alt: Test Coverage
.. image:: https://travis-ci.org/prefeiturasp/SME-PratoAberto-Terceirizadas.svg?branch=development
   :target: https://travis-ci.org/prefeiturasp/SME-PratoAberto-Terceirizadas

Sistema de alimentação focado em terceirizadas


:License: GPLv3


Comandos Básicos
----------------

Carga inicial de dados
^^^^^^^^^^^^^^^^^^^^^^
* Rodar as migrations::

    $ ./manage.py migrate

* Criar o super usuário::

    $ ./manage.py createsuperuser

* Carregar as fixtures::

    $ ./manage.py loaddata sme_pratoaberto_terceirizadas/**/fixtures/*.json

* Carregar dados de planilhas excel junto com pedidos fake::

    $ ./manage.py shell_plus
    $ from utility.carga_dados import run

Verificação de tipos de dados
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  $ mypy sme_pratoaberto_terceirizadas

Test coverage
^^^^^^^^^^^^^

Para executar testes em modo daemon, use o pytest-watch::

    $ ptw
