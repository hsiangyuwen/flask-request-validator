import json
from typing import Any

from flask import make_response

Missing = object()  # Default value instead of using None


def make_json_response(data: Any, status_code: int = 200):
    """JSON dump response data and make_response"""

    resp = make_response(
        json.dumps(data, sort_keys=True, ensure_ascii=False),
        status_code
    )
    resp.mimetype = 'application/json'
    return resp


def make_api_error(
    code: str, message: str = '', data: Any = Missing, *, status_code: int = 500
):
    """Generate api error response"""

    error_obj = {
        'code': code,
        'message': str(message),
    }

    if data is not Missing:
        error_obj['data'] = data

    return make_json_response({'error': error_obj}, status_code=status_code)


def make_api_response(
    data: Any = object(), status_code: int = 200, **kwd
):
    """Generate api success response

    you can pass any data as result

        make_api_response()                    # {"result": null}
        make_api_response(1)                   # {"result": 1}
        make_api_response({'key':'value'})     # {"result": {"key":"value"}}
        make_api_response([{'key1':'value1'}, {'key1':'value2'}])
        # {"results": [{"key1":"value1"}, {"key1":"value2"}]}

    """

    if data is Missing:
        data = kwd if kwd else None

    if isinstance(data, (list, set, tuple)):
        data = dict(results=data)
    else:
        data = dict(result=data)

    return make_json_response(data, status_code)
