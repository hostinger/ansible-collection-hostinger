# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import contextlib
import json
from types import SimpleNamespace
from unittest import mock

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
from ansible_collections.hostinger.vps.plugins.module_utils.api import HostingerApiClient

try:
    from ansible.module_utils.testing import patch_module_args
except ImportError:  # ansible-core < 2.19
    @contextlib.contextmanager
    def patch_module_args(args=None):
        with mock.patch.object(basic, '_ANSIBLE_ARGS', to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': args or {}}))):
            yield


class ModuleExit(Exception):
    def __init__(self, result):
        super().__init__(result)
        self.result = result


def _exit_json(self, **kwargs):
    raise ModuleExit(dict(kwargs, failed=False))


def _fail_json(self, msg, **kwargs):
    raise ModuleExit(dict(kwargs, msg=msg, failed=True))


@pytest.fixture
def run_module(monkeypatch):
    """Run a module's main() with the given arguments and return its result dict."""
    monkeypatch.setattr(basic.AnsibleModule, 'exit_json', _exit_json)
    monkeypatch.setattr(basic.AnsibleModule, 'fail_json', _fail_json)

    def run(module, args):
        with patch_module_args(dict(args, token='test-token')):
            with pytest.raises(ModuleExit) as raised:
                module.main()
        return raised.value.result

    return run


@pytest.fixture
def api(monkeypatch):
    """Replace HTTP calls with canned responses keyed by (method, path) and record every request.

    A response may be a callable taking (body, query), or an exception to raise.
    status_codes sets the HTTP status of a successful response (200 by default).
    """
    fake = SimpleNamespace(calls=[], responses={}, status_codes={})

    def request(self, method, path, body=None, query=None):
        fake.calls.append((method, path, body, query))
        response = fake.responses.get((method, path), {})
        if isinstance(response, Exception):
            raise response
        self.last_status_code = fake.status_codes.get((method, path), 200)
        if callable(response):
            return response(body, query)
        return response

    monkeypatch.setattr(HostingerApiClient, 'request', request)
    return fake
