SME-PratoAberto-Terceirizadas
=============================

.. image:: https://api.codeclimate.com/v1/badges/1f1cdb448bbc3f74efe3/maintainability
   :target: https://codeclimate.com/github/prefeiturasp/SME-PratoAberto-Terceirizadas/maintainability
   :alt: Maintainability
.. image:: https://api.codeclimate.com/v1/badges/1f1cdb448bbc3f74efe3/test_coverage
   :target: https://codeclimate.com/github/prefeiturasp/SME-PratoAberto-Terceirizadas/test_coverage
   :alt: Test Coverage
.. image:: https://travis-ci.org/prefeiturasp/SME-PratoAberto-Terceirizadas.svg?branch=master
   :target: https://travis-ci.org/prefeiturasp/SME-PratoAberto-Terceirizadas

Sistema de alimentação focado em terceirizadas

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django


:License: GPLv3


Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

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

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html





Deployment
----------

The following details how to deploy this application.




