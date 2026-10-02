# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.hostinger.vps.plugins.modules import (
    hostinger_vps_backup,
    hostinger_vps_postinstall_delete,
    hostinger_vps_postinstall_list,
)

SCRIPTS_PATH = '/api/vps/v1/post-install-scripts'


def test_list_returns_scripts_from_every_page(api, run_module):
    pages = {
        1: {'data': [{'id': 1}, {'id': 2}], 'meta': {'current_page': 1, 'per_page': 2, 'total': 3}},
        2: {'data': [{'id': 3}], 'meta': {'current_page': 2, 'per_page': 2, 'total': 3}},
    }
    api.responses[('GET', SCRIPTS_PATH)] = lambda body, query: pages[query['page']]

    result = run_module(hostinger_vps_postinstall_list, {})

    assert result['scripts'] == [{'id': 1}, {'id': 2}, {'id': 3}]


def test_delete_succeeds_on_200_with_message(api, run_module):
    api.responses[('DELETE', SCRIPTS_PATH + '/325')] = {'message': 'Request accepted'}

    result = run_module(hostinger_vps_postinstall_delete, {'post_install_script_id': '325'})

    assert result['failed'] is False
    assert result['changed'] is True


def test_backup_delete_fails_before_calling_the_api(api, run_module):
    result = run_module(hostinger_vps_backup, {'virtual_machine_id': '592873', 'state': 'delete', 'backup_id': '1'})

    assert result['failed'] is True
    assert 'no longer supported' in result['msg']
    assert api.calls == []
