"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import pymysql

# Configurar pymysql como substituto do mysqlclient
pymysql.install_as_MySQLdb()

# Configurar charset UTF-8
pymysql.connections.charset = 'utf8mb4'

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

application = get_wsgi_application()
