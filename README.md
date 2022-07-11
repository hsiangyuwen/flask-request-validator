# Flask Request Validator
*Note: This repository is for PyCon APAC 2022 demo purpose only. Please step into the source code and make your own implementations.*

This is a Flask API request validation helper based on [Cerberus](https://docs.python-cerberus.org/en/stable/index.html) datatype checker.

The request validator is implemented as a python decorator.

## Install and run
```shell
pip install -r requirements.txt
python -m flask run
```

## Usage
Please see **validators.py** for detail information.

## Run test
```shell
pytest
```

## Datatype / Validation Rules Support
Please see [Cerberus - Validation Rules](https://docs.python-cerberus.org/en/stable/validation-rules.html) for detail information.

## How the raised validation error exception handled by Flask app?
There is a base exception class `BaseApiError` which every kind of exceptions are inheriting the base exception. All kinds of exceptions are implemented in `req_validator/exception.py`.

To make the Flask app handle the exception, add an `errorhandler` decorator and put the base exception class (`BaseApiError`) as the argument. This is implemented in `req_validator/__init__.py`.

When the validator wants to raise the error, it puts custom message into `msg` field and `validator.errors` object in `data` field to create the exception instance and raise it.

When the Flask app wants to handle the error, it calls `make_api_error` function to generate the error response. This function is implemented in `req_validator/exceptions.py`.
