"""
Use pytest to run tests

Run `pytest` command at the project root directory.

"""

from enum import Enum
from typing import Dict

import requests

API_BASE_URL = 'http://127.0.0.1:5000/api'  # Flask development server


class Method(str, Enum):
    GET = 'GET'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


def req(method: Method, url: str, *, qs=None, form=None, json=None, files=None, valid_status_code=400) -> Dict:
    if not (form or json or files):
        # Only querystring provided
        resp = requests.request(method.value, url, params=qs)

    if json:
        resp = requests.request(method.value, url, params=qs, json=json)
    if form:
        if files:
            resp = requests.request(
                method.value, url, params=qs, data=form, files=files)
        else:
            resp = requests.request(method.value, url, params=qs, data=form)
    elif files:
        resp = requests.request(method.value, url, params=qs, files=files)

    if resp.status_code != valid_status_code:
        raise AssertionError(resp.text)

    ret_data = resp.json() if valid_status_code == 200 else resp.json()[
        'error']['data']
    return ret_data


##################################################################################################################


def test_validate_qs():
    # Request with an unknown field
    resp_data = req(
        Method.GET, f'{API_BASE_URL}/validate_qs',
        qs={'unknown': 'field'},
    )
    assert resp_data == {'unknown': ['unknown field']}

    # Violates is_date=True
    resp_data = req(
        Method.GET, f'{API_BASE_URL}/validate_qs',
        qs={'date_test': 'invalid_date'},
    )
    assert resp_data == {'date_test': [
        'Must be valid date string YYYY-MM-DD']}

    # Violates allowed. Current allowed value: ['a', 'b', 'c']
    resp_data = req(
        Method.GET, f'{API_BASE_URL}/validate_qs',
        qs={'allowed_test': 'd'},
    )
    assert resp_data == {'allowed_test': ['unallowed value d']}

    # Violates empty
    resp_data = req(
        Method.GET, f'{API_BASE_URL}/validate_qs',
        qs={'empty_test': ''},
    )
    assert resp_data == {'empty_test': ['empty values not allowed']}

    # Correct
    resp_data = req(
        Method.GET, f'{API_BASE_URL}/validate_qs',
        qs={
            'date_test': '2008-09-10',
            'allowed_test': 'a',
            'empty_test': 'non_empty_value',
        },
        valid_status_code=200
    )
    assert resp_data == {"result": "success"}


def test_validate_form():
    # Test trim
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_form',
        form={'leading_space_word': '   hi'},
        valid_status_code=200
    )
    assert resp_data != {"result": {'leading_space_word': '   hi'}}
    assert resp_data == {"result": {'leading_space_word': 'hi'}}

    # Violates regex
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_form',
        form={'email_regex_test': 'abc_at_aaa_dot_aa'}
    )
    assert resp_data == {'email_regex_test': [
        "value does not match regex '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$'"]}

    # dependency test
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_form',
        form={'webhook_url': 'http://example.com/webhook'},
    )
    assert resp_data == {'webhook_url': ["field 'webhook_token' is required"]}

    # Correct
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_form',
        form={
            'email_regex_test': 'abc@aaa.aa',
            'webhook_url': 'http://localhost:3000/webhook',
            'webhook_token': 'token'
        },
        valid_status_code=200
    )
    assert resp_data == {'result': 'success'}


def test_validate_json():
    # Violates contains
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_json',
        json={'contains_test': ['b', 'c', 'd']}
    )
    assert resp_data == {'contains_test': ["missing members {'a'}"]}

    # Violates min/max. Current rule: min: 5, max: 10
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_json',
        json={'min_max_integer_test': 3}
    )
    assert resp_data == {'min_max_integer_test': ['min value is 5']}
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_json',
        json={'min_max_integer_test': 15}
    )
    assert resp_data == {'min_max_integer_test': ['max value is 10']}

    # Violates schema
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_json',
        json={'schema_test': {'name': 'Neal Koblitz', 'phone': '+15198884567'}}
    )
    assert resp_data == {'schema_test': [
        {'enabled': ['required field'], 'phone': ['unknown field']}]}

    # Correct
    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_json',
        json={
            'contains_test': ['a', 'b', 'c'],
            'min_max_integer_test': 8,
            'schema_test': {'name': 'Neal Koblitz', 'enabled': True},
        },
        valid_status_code=200
    )
    assert resp_data == {'result': 'success'}


def test_validate_files():
    test_file = {'file_test': open('tests/valid.jpeg', 'rb')}
    filename = 'valid.jpeg'

    resp_data = req(
        Method.POST, f'{API_BASE_URL}/validate_files',
        files=test_file,
        valid_status_code=200
    )
    assert resp_data == {'result': filename}
