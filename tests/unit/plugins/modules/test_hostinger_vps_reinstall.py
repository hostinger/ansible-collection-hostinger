# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.hostinger.vps.plugins.modules import hostinger_vps_reinstall

RECREATE_PATH = '/api/vps/v1/virtual-machines/592873/recreate'


def test_sends_snake_case_payload_with_integer_ids(api, run_module):
    api.responses[('POST', RECREATE_PATH)] = {'id': 8123, 'name': 'recreate', 'state': 'sent'}

    result = run_module(hostinger_vps_reinstall, {
        'virtual_machine_id': '592873',
        'template_id': '1121',
        'password': 'Sup3r-Secret-Pass',
        'post_install_script_id': '42',
    })

    assert result['failed'] is False
    assert result['action']['id'] == 8123
    assert api.calls == [
        ('POST', RECREATE_PATH, {'template_id': 1121, 'password': 'Sup3r-Secret-Pass', 'post_install_script_id': 42}, None),
    ]


def test_omits_unset_options(api, run_module):
    run_module(hostinger_vps_reinstall, {'virtual_machine_id': '592873', 'template_id': 1121})

    assert api.calls == [('POST', RECREATE_PATH, {'template_id': 1121}, None)]


def test_public_ssh_key_id_fails_before_calling_the_api(api, run_module):
    result = run_module(hostinger_vps_reinstall, {
        'virtual_machine_id': '592873',
        'template_id': 1121,
        'public_ssh_key_id': '7',
    })

    assert result['failed'] is True
    assert 'hostinger_vps_ssh_key_binding' in result['msg']
    assert api.calls == []
