#!/usr/bin/env python


import os
import sys
from pathlib import Path
from fermerce.core.settings import config
from esmerald import Esmerald, Include
from edgy import Migrate


def build_path():
    Path(__file__).resolve().parent.parent
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

    if SITE_ROOT not in sys.path:
        sys.path.append(SITE_ROOT)
        sys.path.append(os.path.join(SITE_ROOT, "fermerce"))


def get_application():
    build_path()
    database, registry = config.database_config

    app = Esmerald(
        routes=[Include(namespace="fermerce.core.router.v1")],
        on_startup=[database.connect],
        on_shutdown=[database.disconnect],
    )

    Migrate(app=app, registry=registry)
    return app


app = get_application()
