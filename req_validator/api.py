from flask import Blueprint, request

from .response import make_api_response
from .validators import req_validator

bp = Blueprint('api', __name__)


@bp.route('/validate_qs', methods=["GET", "POST"])
@req_validator(
    qs={
        'date_test': dict(type='string', is_date=True),
        'allowed_test': dict(type='string', allowed=['a', 'b', 'c']),
        'empty_test': dict(type='string', empty=False)
    }
)
def validate_qs():
    """
    type:
        string

    validation rules:
        is_date (custom)
        allowed
        empty
    """

    # TODO: Actual implementations

    return make_api_response('success')


@bp.route('/validate_form', methods=["POST"])
@req_validator(
    form={
        'leading_space_word': dict(type='string', coerce='trim'),
        'email_regex_test': dict(type='string', regex='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'),
        'webhook_url': dict(type='string', required=False, nullable=True, dependencies='webhook_token'),
        'webhook_token': dict(type='string', required=False, nullable=True, dependencies='webhook_url')
    }
)
def validate_form():
    """
    type:
        string

    validation rules:
        trim (coerce)
        regex
        dependencies
    """
    req_data = request.f

    # TODO: Actual implementations

    if 'leading_space_word' in req_data:
        ret = {'leading_space_word': req_data['leading_space_word']}
    else:
        ret = 'success'

    return make_api_response(ret)


@bp.route('/validate_json', methods=["POST"])
@req_validator(
    json={
        'contains_test': dict(type='list', contains=['a', 'b']),
        'min_max_integer_test': dict(type='integer', min=5, max=10),
        'schema_test': dict(type='dict', schema={
            'name': dict(type='string', required=True),
            'enabled': dict(type='boolean', required=True)
        }),
    }
)
def validate_json():
    """
    type:
        boolean
        dict
        integer
        list

    validation rules:
        contains
        min, max
        schema
    """

    # TODO: Actual implementations

    return make_api_response('success')


@bp.route('/validate_files', methods=["POST"])
@req_validator(
    files={'file_test': True}
)
def validate_files():
    """
    Not utilizing cerberus validator
    """
    try:
        test_file = request.files['file_test']
    except KeyError as err:
        raise err

    return make_api_response(test_file.filename)
