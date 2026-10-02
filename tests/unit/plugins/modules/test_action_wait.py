# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import time
from types import SimpleNamespace

import pytest

from ansible_collections.hostinger.vps.plugins.module_utils import api as api_utils
from ansible_collections.hostinger.vps.plugins.modules import (
    hostinger_vps_malware_scanner,
    hostinger_vps_power,
    hostinger_vps_snapshot,
)

VM_PATH = '/api/vps/v1/virtual-machines/592873'
ACTION_PATH = VM_PATH + '/actions/8123'


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(api_utils, 'time', SimpleNamespace(monotonic=time.monotonic, sleep=lambda seconds: None))


def action_states(*states):
    """Return a fake response that reports the given states on successive polls."""
    remaining = list(states)

    def respond(body, query):
        return {'id': 8123, 'name': 'ct_restart', 'state': remaining.pop(0)}

    return respond


def test_without_wait_the_started_action_is_returned(api, run_module):
    api.responses[('POST', VM_PATH + '/restart')] = {'id': 8123, 'name': 'ct_restart', 'state': 'sent'}

    result = run_module(hostinger_vps_power, {'virtual_machine_id': '592873', 'action': 'restart'})

    assert result['response']['state'] == 'sent'
    assert [call[1] for call in api.calls] == [VM_PATH + '/restart']


def test_wait_returns_the_finished_action(api, run_module):
    api.responses[('POST', VM_PATH + '/restart')] = {'id': 8123, 'name': 'ct_restart', 'state': 'sent'}
    api.responses[('GET', ACTION_PATH)] = action_states('sent', 'success')

    result = run_module(hostinger_vps_power, {'virtual_machine_id': '592873', 'action': 'restart', 'wait': True})

    assert result['failed'] is False
    assert result['response']['state'] == 'success'
    assert [call[1] for call in api.calls] == [VM_PATH + '/restart', ACTION_PATH, ACTION_PATH]


def test_wait_fails_the_module_when_the_action_fails(api, run_module):
    api.responses[('POST', VM_PATH + '/restart')] = {'id': 8123, 'name': 'ct_restart', 'state': 'sent'}
    api.responses[('GET', ACTION_PATH)] = action_states('error')

    result = run_module(hostinger_vps_power, {'virtual_machine_id': '592873', 'action': 'restart', 'wait': True})

    assert result['failed'] is True
    assert "Power action 'restart' failed" in result['msg']
    assert result['response']['state'] == 'error'


def test_malware_scanner_keeps_the_status_code_of_the_install_call(api, run_module):
    api.responses[('POST', VM_PATH + '/monarx')] = {'id': 8123, 'name': 'monarx_install', 'state': 'sent'}
    api.status_codes[('POST', VM_PATH + '/monarx')] = 201
    api.responses[('GET', ACTION_PATH)] = action_states('success')

    result = run_module(hostinger_vps_malware_scanner, {'virtual_machine_id': 592873, 'scanner_action': 'install', 'wait': True})

    assert result['status_code'] == 201
    assert result['response']['state'] == 'success'


def test_snapshot_get_ignores_wait(api, run_module):
    api.responses[('GET', VM_PATH + '/snapshot')] = {'id': 325, 'restore_time': 1800}

    result = run_module(hostinger_vps_snapshot, {'virtual_machine_id': '592873', 'state': 'get', 'wait': True})

    assert result['snapshot'] == {'id': 325, 'restore_time': 1800}
    assert len(api.calls) == 1
