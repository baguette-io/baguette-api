baguette REST api for web and client.


Setup
=====

Configuration file
------------------

You have to create */etc/boulangerie.ini*
which must contains these keys:

::

    [general]
    debug=0
    static_url=/static/
    static_root=/data/static/
    uri_template=git@git.baguette.io:{0}.{1}.git

    [database]
    name=baguette
    engine=django.db.backends.postgresql
    user=jambon
    password=beurre
    host=127.0.0.1
    port=5432

    [broker]
    uri=amqp://127.0.0.1:5672/amqp

    [cuisson]
    amqp_uri=amqp://jambon:beurre@127.0.0.1/baguette

    [defournement]
    amqp_uri=amqp://jambon:beurre@127.0.0.1/baguette

    [security]
    secret_key=<key>
    allowed_host=<allowed>

    [quotas]
    max_keys=100
    max_projects=100
    max_vpcs=10
    max_organizations=10

You can override the path using **BOULANGERIE_INI**.

Install
-------

::

    [baguette-api]$ virtualenv venv
    [baguette-api]$ source venv/bin/activate
    [(venv) baguette-api]$ python setup.py develop
    [(venv) baguette-api]$ pip install -e .[testing]
    [(venv) baguette-api]$ pip install -e .[doc]


Admin token
-----------

::

    [(venv) boulangerie]$ boulangerie createsuperuser
    Username: admin
    Email: admin@baguette.io
    Password: 
    Password (again): 
    Superuser created successfully.
    [(venv) boulangerie]$ boulangerie shell
    boulangerie shell 
    Python 2.7.13 (default, Nov 24 2017, 17:33:09) 
    [GCC 6.3.0 20170516] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> from boulangerie.apps.accounts.models import Account
    >>> from rest_framework_jwt.settings import api_settings
    >>> user = Account.objects.get(username='admin')
    >>> jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    >>> jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    >>> payload = jwt_payload_handler(user)
    >>> payload['exp'] = payload['exp'].replace(year=payload['exp'].year + 30)
    >>> token = jwt_encode_handler(payload)
    
Database
--------

To synchronize the database:

::

    [(venv) boulangerie]$ python manage.py migrate
    [(venv) boulangerie]$ python manage.py createsuperuser


Launch
------

To launch the api:

::

    [(venv) boulangerie]$ boulangerie runserver


Creating an user using the API
------------------------------

::

    [(venv) boulangerie]$ curl -X POST -H "Content-Type:application/json" -d '{"username":"test", "email":"test@test.test", "password":"test@test.test", "confirm_password":"test@test.test"}' http://127.0.0.1:8000/api/v1/account/register/


Login with an user using the API
--------------------------------

::

    [(venv) boulangerie]$ curl -X POST -H "Content-Type:application/json" -d '{"email":"test@test.test", "password":"test@test.test"}' http://127.0.0.1:8000/api/v1/account/login/

Create an app using the API
---------------------------

::

    [(venv) boulangerie]$ curl -X POST -H "Authorization: JWT <token>" -H 'Content-Type: application/json'  -d '{"name":"test"}' http://127.0.0.1:8000/api/v1/application/apps/ 

List the apps using the API
---------------------------

::

    [(venv) boulangerie]$ curl -H "Authorization: JWT <token>" -H 'Content-Type: application/json' http://127.0.0.1:8000/api/v1/application/apps/ 

Details of an app using the API
-------------------------------

::

    [(venv) boulangerie]$ curl -H "Authorization: JWT <token>" -H 'Content-Type: application/json' http://127.0.0.1:8000/api/v1/application/apps/<app_name>/

Delete an app using the API
---------------------------

::

    [(venv) boulangerie]$ curl -X DELETE -H "Authorization: JWT <token>" -H 'Content-Type: application/json' http://127.0.0.1:8000/api/v1/application/apps/<app_name>/

Create a branch using the API
-----------------------------

::

    [(venv) boulangerie]$ curl -X POST -H "Authorization: JWT <token>" -H 'Content-Type: application/json'  -d '{"name":"test", "app":"<app_name>"}' http://127.0.0.1:8000/api/v1/application/branches/

List the branches using the API
-------------------------------

::

    [(venv) boulangerie]$ curl -H "Authorization: JWT <token>" -H 'Content-Type: application/json' http://127.0.0.1:8000/api/v1/application/branches/

Details of a branch using the API
---------------------------------

::

    [(venv) boulangerie]$ curl -H "Authorization: JWT <token>" -H 'Content-Type: application/json' http://127.0.0.1:8000/api/v1/application/branches/<branch_uri>/

Delete a branch using the API
-----------------------------

::

    [(venv) boulangerie]$ curl -X DELETE -H "Authorization: JWT <token>" -H 'Content-Type: application/json' http://127.0.0.1:8000/api/v1/application/branches/<branch_uri>/

