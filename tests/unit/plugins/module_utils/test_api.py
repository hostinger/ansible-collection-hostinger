# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import io
import json
from urllib.error import HTTPError, URLError

import pytest

from ansible_collections.hostinger.vps.plugins.module_utils import api
from ansible_collections.hostinger.vps.plugins.module_utils.api import HostingerApiClient, HostingerApiError


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def read(self):
        return self.body

    def getcode(self):
        return self.status


def http_error(code, body):
    return HTTPError('https://developers.hostinger.com/x', code, 'reason', {}, io.BytesIO(body))


@pytest.fixture
def open_url(monkeypatch):
    calls = []
    responses = []

    def fake_open_url(url, **kwargs):
        calls.append(dict(kwargs, url=url))
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(api, 'open_url', fake_open_url)
    return calls, responses


def test_request_sends_json_with_token_and_user_agent(open_url):
    calls, responses = open_url
    responses.append(FakeResponse(b'{"id": 1}'))

    result = HostingerApiClient('secret', api_url='https://example.test/').post('/api/x', body={'name': 'a'})

    assert result == {'id': 1}
    assert calls[0]['url'] == 'https://example.test/api/x'
    assert calls[0]['method'] == 'POST'
    assert json.loads(calls[0]['data']) == {'name': 'a'}
    assert calls[0]['headers']['Authorization'] == 'Bearer secret'
    assert calls[0]['http_agent'] == 'ansible-collection-hostinger'


def test_request_encodes_query_and_returns_empty_dict_for_empty_body(open_url):
    calls, responses = open_url
    responses.append(FakeResponse(b''))

    assert HostingerApiClient('secret').get('/api/x', query={'date_from': '2025-01-01'}) == {}
    assert calls[0]['url'].endswith('/api/x?date_from=2025-01-01')
    assert calls[0]['data'] is None


def test_validation_error_lists_field_errors(open_url):
    responses = open_url[1]
    responses.append(http_error(422, json.dumps({
        'message': 'The protocol field is required. (and 1 more error)',
        'errors': {'protocol': ['The protocol field is required.'], 'port': ['The port field is required.']},
    }).encode()))

    with pytest.raises(HostingerApiError) as raised:
        HostingerApiClient('secret').post('/api/vps/v1/firewall/1/rules', body={})

    assert raised.value.status_code == 422
    assert raised.value.response['errors']['port'] == ['The port field is required.']
    assert 'POST /api/vps/v1/firewall/1/rules returned HTTP 422' in str(raised.value)
    assert 'protocol: The protocol field is required.; port: The port field is required.' in str(raised.value)


def test_non_json_error_body_is_kept_as_text(open_url):
    responses = open_url[1]
    responses.append(http_error(403, b'<html>Sorry, you have been blocked</html>'))

    with pytest.raises(HostingerApiError) as raised:
        HostingerApiClient('secret').get('/api/x')

    assert raised.value.status_code == 403
    assert 'Sorry, you have been blocked' in str(raised.value)


def test_network_error_has_no_status_code(open_url):
    responses = open_url[1]
    responses.append(URLError('timed out'))

    with pytest.raises(HostingerApiError) as raised:
        HostingerApiClient('secret').get('/api/x')

    assert raised.value.status_code is None
    assert 'GET /api/x failed: timed out' in str(raised.value)


def test_get_all_pages_follows_pagination(open_url):
    calls, responses = open_url
    responses.append(FakeResponse(json.dumps({'data': [1, 2], 'meta': {'current_page': 1, 'per_page': 2, 'total': 3}}).encode()))
    responses.append(FakeResponse(json.dumps({'data': [3], 'meta': {'current_page': 2, 'per_page': 2, 'total': 3}}).encode()))

    assert HostingerApiClient('secret').get_all_pages('/api/x') == [1, 2, 3]
    assert [call['url'].split('?')[1] for call in calls] == ['page=1', 'page=2']


def test_missing_token_is_rejected():
    with pytest.raises(HostingerApiError, match='HOSTINGER_API_TOKEN'):
        HostingerApiClient('')
