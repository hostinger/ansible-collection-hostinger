# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible_collections.hostinger.vps.plugins.modules import (
    hostinger_vps_backup,
    hostinger_vps_firewall_rule,
    hostinger_vps_power,
)

PATH_CHANGING_ID = '1/../../billing/v1/subscriptions/1'


@pytest.mark.parametrize('module, args', [
    (hostinger_vps_power, {'virtual_machine_id': PATH_CHANGING_ID, 'action': 'stop'}),
    (hostinger_vps_backup, {'virtual_machine_id': 1, 'backup_id': PATH_CHANGING_ID, 'state': 'restore'}),
    (hostinger_vps_firewall_rule, {'firewall_id': 1, 'rule_id': PATH_CHANGING_ID, 'state': 'delete'}),
])
def test_ids_that_are_not_integers_are_rejected_before_any_request(api, run_module, module, args):
    result = run_module(module, args)

    assert result['failed']
    assert 'int' in result['msg']
    assert api.calls == []
