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


Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy sme_pratoaberto_terceirizadas

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest



Deployment
----------

...



