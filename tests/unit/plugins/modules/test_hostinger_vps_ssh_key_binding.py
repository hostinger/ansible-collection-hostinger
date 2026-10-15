# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.hostinger.vps.plugins.modules import hostinger_vps_ssh_key_binding

SSH_KEYS_PATH = '/api/vps/v1/virtual-machines/592873/ssh-keys'
KEY = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA user@host'


def test_sends_key_text_to_the_ssh_keys_endpoint(api, run_module):
    api.responses[('POST', SSH_KEYS_PATH)] = [{'key': KEY, 'name': 'user@host'}]

    result = run_module(hostinger_vps_ssh_key_binding, {'virtual_machine_id': '592873', 'keys': [KEY]})

    assert result['failed'] is False
    assert result['result'] == [{'key': KEY, 'name': 'user@host'}]
    assert api.calls == [('POST', SSH_KEYS_PATH, {'keys': [KEY]}, None)]
