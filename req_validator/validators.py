import datetime
from functools import wraps

from cerberus import Validator
from flask import request
from werkzeug.exceptions import BadRequest

from .exceptions import (
    InvalidQueryStringError, InvalidFormDataError, InvalidJsonError, InvalidFilesError,
    BaseApiError
)


class MyValidator(Validator):
    """
    Extend cerberus rules to support custom rules and custom normalization

    Reference: https://docs.python-cerberus.org/en/stable/customize.html
    """

    def _validate_is_date(self, is_date, field, value):
        """ Test if the value is a date string (YYYY-MM-DD)

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if is_date and value is not None:
            try:
                datetime.date.fromisoformat(value)
            except (TypeError, ValueError):
                self._error(field, 'Must be valid date string YYYY-MM-DD')

    def _normalize_coerce_trim(self, value):
        """ Trim the value before the validator process the document.

        Example: '  abcde    ' --> 'abcde'

        Usage: json = {'sender_str': dict(type='string', coerce = 'trim')}

        The `value` passed in could be any type but only the str type will be trimmed
        """

        if isinstance(value, str):
            return value.strip()
        else:
            return value


class req_validator:
    """ A decorator to validate Flask request object

    :param qs: cerberus rules to validate query string (``request.args``). You can access ``request.q`` to get the normalized parameters
    :param form: cerberus rules to validate form data (``request.form``). You can access ``request.f`` to get the normalized parameters
    :param json: cerberus rules to validate form body in json format (``request.get_json(True)``). You can access ``request.j`` to get the normalized parameters
    :param files: name of files and if it is required (``request.files``)

    See http://docs.python-cerberus.org/en/stable/validation-rules.html for available rules.

    Some extended rules are:

    * is_date (`dict(type='string', is_date=True)`) Validate if the string follows the YYYY-MM-DD format
    * trim (`dict(type='string', ..., coerce='trim')`) Remove space characters at the beginning and at the end of the string

    """

    __slots__ = [
        'qs_validator',
        'form_validator',
        'json_validator',
        'files',
    ]

    def __init__(self, *, qs=None, form=None, json=None, files=None):
        """ Definitions of the parameters of the request validator

        qs:   HTTP GET/POST querystring(URL encoded parameters) 
        form: HTTP POST payload content type: application/x-www-form-urlencoded or multipart/form-data
        json: HTTP POST payload content type: application/json
        """

        if json is not None:
            if form is not None:
                msg = "You can't have 'form' and 'json' at the same time"
                raise BaseApiError(msg)
            if files is not None:
                msg = "You can't have 'files' and 'json' at the same time"
                raise BaseApiError(msg)

        self.qs_validator = MyValidator(qs) if qs is not None else None
        self.form_validator = MyValidator(form) if form is not None else None
        self.json_validator = MyValidator(json) if json is not None else None
        # The validator is not involved. Only check for file existence.
        self.files = files or None

    @classmethod
    def _validate(cls, validator, data, error_cls, fname):
        valid = validator.validate(data)
        if not valid and request.method != 'OPTIONS':
            msg = f"Invalid input format for '{fname}'"
            raise error_cls(msg, data=validator.errors)
        else:
            return validator.normalized(data)

    def __call__(self, f):

        @wraps(f)
        def wrapper(*arg, **kwd):
            fname = f.__name__

            if self.qs_validator is not None:
                request.q = dict(request.args)
                request.q = self._validate(
                    self.qs_validator, request.q, InvalidQueryStringError, fname)

            if self.form_validator is not None:
                request.f = dict(request.form)
                request.f = self._validate(
                    self.form_validator, request.f, InvalidFormDataError, fname)

            try:
                input_json = request.get_json(True)
            except BadRequest:
                input_json = {}

            if self.json_validator is not None:
                request.j = self._validate(
                    self.json_validator, input_json, InvalidJsonError, fname)

            # Only check for file existence
            if self.files is not None:
                for field_name, is_required in self.files.items():
                    if is_required and field_name not in request.files:
                        msg = f"Invalid input format for '{fname}'"
                        raise InvalidFilesError(msg, data=field_name)

            return f(*arg, **kwd)

        return wrapper
