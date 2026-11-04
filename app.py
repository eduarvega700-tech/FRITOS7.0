"""FRITOS TECH: punto de entrada. Solo arma la aplicación."""
import os
from datetime import datetime

from flask import Flask

import db
import urls
from config import Config
from helpers import formato_cop, token_csrf, verificar_csrf
from views import errores


def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")

    db.init_app(app)

    app.template_filter("cop")(formato_cop)
    app.before_request(verificar_csrf)
    app.context_processor(
        lambda: {"anio": datetime.now().year, "csrf_token": token_csrf}
    )

    errores.registrar(app)
    urls.registrar_urls(app)
    return app


app = crear_app()

if __name__ == "__main__":
    app.run(debug=True)
