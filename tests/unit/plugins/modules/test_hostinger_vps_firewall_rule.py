# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible_collections.hostinger.vps.plugins.modules import hostinger_vps_firewall_rule
from ansible_collections.hostinger.vps.plugins.modules.hostinger_vps_firewall_rule import normalize_protocol


@pytest.mark.parametrize('given, expected', [
    ('tcp', 'TCP'),
    ('any', 'any'),
    ('ANY', 'any'),
    ('icmpv6', 'ICMPv6'),
    ('mysql', 'MySQL'),
    ('PostgreSQL', 'PostgreSQL'),
    ('telnet', None),
])
def test_normalize_protocol(given, expected):
    assert normalize_protocol(given) == expected


def test_create_sends_protocol_in_api_casing(api, run_module):
    rule = {'protocol': 'mysql', 'port': '3306', 'source': 'any', 'source_detail': 'any'}

    result = run_module(hostinger_vps_firewall_rule, {'firewall_id': '72122', 'state': 'create', 'rule': rule})

    assert result['changed'] is True
    assert api.calls == [('POST', '/api/vps/v1/firewall/72122/rules', dict(rule, protocol='MySQL'), None)]


def test_invalid_protocol_fails_before_calling_the_api(api, run_module):
    rule = {'protocol': 'telnet', 'port': '23', 'source': 'any', 'source_detail': 'any'}

    result = run_module(hostinger_vps_firewall_rule, {'firewall_id': '72122', 'state': 'create', 'rule': rule})

    assert result['failed'] is True
    assert api.calls == []
