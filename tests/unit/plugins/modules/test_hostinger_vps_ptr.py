# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible_collections.hostinger.vps.plugins.modules import hostinger_vps_ptr
from ansible_collections.hostinger.vps.plugins.modules.hostinger_vps_ptr import find_ip_address_id

VM_PATH = '/api/vps/v1/virtual-machines/592873'
VM = {
    'id': 592873,
    'ipv4': [{'id': 1536360, 'address': '187.124.131.134'}],
    'ipv6': [{'id': 847786, 'address': '2a02:4780:c:b6fd::1'}],
}


def test_defaults_to_the_only_ipv4_address():
    assert find_ip_address_id(VM) == 1536360


def test_matches_ipv6_address_in_any_notation():
    assert find_ip_address_id(VM, '2a02:4780:000c:b6fd:0000:0000:0000:0001') == 847786


def test_requires_ip_address_when_there_are_several_ipv4_addresses():
    vm = dict(VM, ipv4=[{'id': 1, 'address': '203.0.113.1'}, {'id': 2, 'address': '203.0.113.2'}])

    with pytest.raises(ValueError, match='has 2 IPv4 addresses'):
        find_ip_address_id(vm)


def test_rejects_address_that_is_not_assigned():
    with pytest.raises(ValueError, match='not assigned'):
        find_ip_address_id(VM, '203.0.113.99')


def test_sets_ptr_as_domain_on_the_ip_address_endpoint(api, run_module):
    api.responses[('GET', VM_PATH)] = VM

    result = run_module(hostinger_vps_ptr, {'virtual_machine_id': 592873, 'ptr': 'mail.example.com'})

    assert result['changed'] is True
    assert api.calls[-1] == ('POST', VM_PATH + '/ptr/1536360', {'domain': 'mail.example.com'}, None)


def test_deletes_ptr_of_the_ip_address(api, run_module):
    api.responses[('GET', VM_PATH)] = VM

    run_module(hostinger_vps_ptr, {'virtual_machine_id': 592873})

    assert api.calls[-1] == ('DELETE', VM_PATH + '/ptr/1536360', None, None)
