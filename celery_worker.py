# -*- encoding: utf-8 -*-
from flask.helpers import get_debug_flag

from analyzerapp.celery import create_celery

from analyzerapp.app import create_app
from analyzerapp.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

celery = create_celery(create_app(CONFIG))