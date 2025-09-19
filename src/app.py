import os
import logging

from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from pydantic import BaseModel

from src.config import config
from src.exceptions import ModuleException
from src.injectors.connections import setup_pg
from src.models import *  # noqa
from src.routers import files_routers


def setup_app() -> Flask:
    current_app = Flask(__name__)
    setup_pg()
    if config.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    return current_app


class PydanticJSONEncoder(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)


app = setup_app()
app.register_blueprint(files_routers)
app.json = PydanticJSONEncoder(app)


@app.errorhandler(ModuleException)
def handle_app_exception(e: ModuleException):
    if e.code == 500 or config.debug:
        import traceback

        traceback.print_exc()
    return jsonify(e.json()), e.code


if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "0.0.0.0"),
        debug=config.debug,
    )
