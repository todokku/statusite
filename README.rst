statusite
=========

A simple Django status site for Salesforce managed package projects hosted on Github

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django


:License: BSD

Setup
-----

Set up a virtualenv however you usually do that (for example)::

    $ python3 -m venv ../envs/statusite-py3

Activate it directly or through a .envrc (direnv)::

    $ source ../envs/statusite-py3/bin/activate

While you're at it, set the DJANGO_READ_DOT_ENV_FILE environment variable 
(direnv might be a good way to make this persistent)::

    $ export DJANGO_READ_DOT_ENV_FILE=True

Setup your environment::

    $ pip install -r requirements/local.txt
    $ cp env.example .env
    $ code .env
    $ # make necessary edits
    $ ./manage.py createdatabase
    $ echo "CREATE DATABASE statusite WITH ENCODING 'UTF-8';"  | psql
    $ ./manage.py migrate

Now you'll want to set up your users as described below.

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Running tests
^^^^^^^^^^^^^

To run the tests and generate a coverage report::

    $ redis-server # if it isn't already running
    $ coverage erase
    $ coverage run pytest
    $ coverage report -m


Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html


Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html



Sentry
^^^^^^

Sentry is an error logging aggregator service. You can sign up for a free account at  https://sentry.io/signup/?code=cookiecutter  or download and host it yourself.
The system is setup with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.


Deployment
----------

The following details how to deploy this application.


Heroku
^^^^^^

See detailed `cookiecutter-django Heroku documentation`_.

.. _`cookiecutter-django Heroku documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html
