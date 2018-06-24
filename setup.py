#-*- coding:utf-8 -*-
"""
Setup for baguette-api package (aka: boulangerie).
"""
from setuptools import find_packages, setup

setup(
    name='baguette-api',
    version='0.1',
    url='baguette.io',
    author_email='dev@baguette.io',
    packages=find_packages(),
    platforms=[
        'Linux/UNIX',
        'MacOS',
        'Windows'
    ],
    install_requires=[
        'baguette-messaging',
        'Django==1.11.3',
        'djangorestframework==3.4.1',
        'dry-rest-permissions==0.1.6',
        'djangorestframework-jwt==1.8.0',
        'django-cors-headers==1.2.2',
        'django-crispy-forms==1.6.0',
        'django-filter==1.0.2',
        'django-guardian==1.4.9',
        'django-signal-disabler==0.1.1',
        'Markdown==2.6.6',
        'psycopg2==2.6.2',
        'sshpubkeys==2.2.0',
    ],
    entry_points={
        'console_scripts':[
            'boulangerie=boulangerie.manage:main',
        ],
    },
    extras_require={
        'testing': [
            'baguette-messaging[testing]',
            'mock',
            'pytest',
            'pytest-cov',
            'pytest-django==3.0.0',
            'pytest-rabbitmq',
            'pylint==1.6.1',
            'rabbitpy==0.26.2',
        ],
        'doc': [
            'Sphinx==1.4.4',
        ],
    },
)
