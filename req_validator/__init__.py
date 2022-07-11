from flask import Flask

from .api import bp as bp_api
from .exceptions import BaseApiError
from .response import make_api_error


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp_api, url_prefix='/api')

    @app.errorhandler(BaseApiError)
    def handle_api_error(error):
        return make_api_error(
            code=error.CODE,
            message=error.MESSAGE if error.msg is None else error.msg,
            data=error.data,
            status_code=error.STATUS_CODE
        )

    return app
