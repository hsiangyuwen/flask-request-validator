from typing import Optional


class BaseApiError(Exception):
    """ Generic error of all API.

    Http status 500 (Internal Error)
    """
    CODE: str = "GENERIC"
    STATUS_CODE: int = 500
    MESSAGE: Optional[str] = None

    def __init__(self, msg: str = "", data=None):
        super().__init__(msg, data)
        self.msg = msg
        self.data = data


class InvalidInputError(BaseApiError):
    """ Input data is invalid or has wrong format.

    Http status 400 (Bad Request)
    """
    CODE = "INVALID_INPUT_FORMAT"
    STATUS_CODE = 400


class InvalidQueryStringError(InvalidInputError):
    """Input data in *query string* has wrong format"""
    CODE = "INVALID_INPUT_FORMAT_QUERYSTRING"


class InvalidFormDataError(InvalidInputError):
    """Input data in *form data* has wrong format"""
    CODE = "INVALID_INPUT_FORMAT_FORMDATA"


class InvalidJsonError(InvalidInputError):
    """Input data in *JSON body* has wrong format"""
    CODE = "INVALID_INPUT_FORMAT_JSON"


class InvalidFilesError(InvalidInputError):
    """Upload file missing or unacceptable file type"""
    CODE = "INVALID_INPUT_FORMAT_FILES"
