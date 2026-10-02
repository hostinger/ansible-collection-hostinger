# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.hostinger.vps.plugins.module_utils.api import HostingerApiError
from ansible_collections.hostinger.vps.plugins.modules import (
    hostinger_vps_action_info,
    hostinger_vps_catalog_info,
    hostinger_vps_malware_scanner_info,
    hostinger_vps_snapshot_info,
    hostinger_vps_vm_info,
)

VM_PATH = '/api/vps/v1/virtual-machines/592873'


def test_vm_info_without_id_lists_every_virtual_machine(api, run_module):
    api.responses[('GET', '/api/vps/v1/virtual-machines')] = [{'id': 1}, {'id': 592873}]

    result = run_module(hostinger_vps_vm_info, {})

    assert result['changed'] is False
    assert result['virtual_machines'] == [{'id': 1}, {'id': 592873}]


def test_vm_info_with_id_returns_a_single_item_list(api, run_module):
    api.responses[('GET', VM_PATH)] = {'id': 592873}

    result = run_module(hostinger_vps_vm_info, {'virtual_machine_id': 592873})

    assert result['virtual_machines'] == [{'id': 592873}]


def test_action_info_collects_every_page(api, run_module):
    pages = {
        1: {'data': [{'id': 3}, {'id': 2}], 'meta': {'current_page': 1, 'per_page': 2, 'total': 3}},
        2: {'data': [{'id': 1}], 'meta': {'current_page': 2, 'per_page': 2, 'total': 3}},
    }
    api.responses[('GET', VM_PATH + '/actions')] = lambda body, query: pages[query['page']]

    result = run_module(hostinger_vps_action_info, {'virtual_machine_id': 592873})

    assert [action['id'] for action in result['actions']] == [3, 2, 1]


def test_catalog_info_sends_only_the_filters_that_are_set(api, run_module):
    run_module(hostinger_vps_catalog_info, {'category': 'VPS'})
    run_module(hostinger_vps_catalog_info, {'name': 'KVM*'})

    assert [call[3] for call in api.calls] == [{'category': 'VPS'}, {'name': 'KVM*'}]


def test_snapshot_info_returns_null_for_the_no_snapshot_placeholder(api, run_module):
    # Observed from the live API for a virtual machine without a snapshot.
    api.responses[('GET', VM_PATH + '/snapshot')] = {
        'id': 0, 'restore_time': 0, 'created_at': '2026-10-02T08:11:27Z', 'expires_at': '2026-10-02T08:11:27Z',
    }

    result = run_module(hostinger_vps_snapshot_info, {'virtual_machine_id': 592873})

    assert result['snapshot'] is None


def test_snapshot_info_returns_an_existing_snapshot(api, run_module):
    api.responses[('GET', VM_PATH + '/snapshot')] = {'id': 325, 'restore_time': 1800}

    result = run_module(hostinger_vps_snapshot_info, {'virtual_machine_id': 592873})

    assert result['snapshot'] == {'id': 325, 'restore_time': 1800}


def test_malware_scanner_info_reports_a_missing_scanner(api, run_module):
    api.responses[('GET', VM_PATH + '/monarx')] = HostingerApiError(
        'not installed', status_code=422, response={'message': '[VPS:2042] Monarx is not installed.'},
    )

    result = run_module(hostinger_vps_malware_scanner_info, {'virtual_machine_id': 592873})

    assert result['failed'] is False
    assert result['installed'] is False
    assert result['metrics'] is None


def test_malware_scanner_info_fails_on_other_validation_errors(api, run_module):
    api.responses[('GET', VM_PATH + '/monarx')] = HostingerApiError(
        'other', status_code=422, response={'message': '[VPS:2001] Something else.'},
    )

    result = run_module(hostinger_vps_malware_scanner_info, {'virtual_machine_id': 592873})

    assert result['failed'] is True


def test_malware_scanner_info_returns_metrics_when_installed(api, run_module):
    api.responses[('GET', VM_PATH + '/monarx')] = {'malicious': 0, 'scanned_files': 193218}

    result = run_module(hostinger_vps_malware_scanner_info, {'virtual_machine_id': 592873})

    assert result['installed'] is True
    assert result['metrics']['scanned_files'] == 193218
