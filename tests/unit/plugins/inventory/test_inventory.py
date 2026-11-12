# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest import mock

import pytest

from ansible.errors import AnsibleError
from ansible.inventory.data import InventoryData
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

try:
    from ansible.template import trust_as_template
except ImportError:  # ansible-core < 2.19 templates every string
    def trust_as_template(value):
        return value

from ansible_collections.hostinger.vps.plugins.inventory.inventory import InventoryModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import HostingerApiClient, HostingerApiError


def vm(vm_id, hostname, **fields):
    return dict({'id': vm_id, 'hostname': hostname, 'ipv4': [{'address': f'10.0.0.{vm_id}'}]}, **fields)


@pytest.fixture
def parse(monkeypatch):
    """Run the plugin against a fake API response and return the inventory and the warnings it logged."""
    def run(response):
        def get(self, path, query=None):
            if isinstance(response, Exception):
                raise response
            return response

        monkeypatch.setattr(HostingerApiClient, 'get', get)
        monkeypatch.setattr(InventoryModule, '_read_config_data', lambda self, path: None)
        options = {'token': 'test-token', 'api_url': None, 'api_timeout': None}
        monkeypatch.setattr(InventoryModule, 'get_option', lambda self, name: options[name])

        plugin = InventoryModule()
        plugin.display = mock.Mock()
        inventory = InventoryData()
        plugin.parse(inventory, DataLoader(), 'hostinger.yml')
        warnings = [call.args[0] for call in plugin.display.warning.call_args_list]
        return inventory, warnings

    return run


def test_vms_are_added_with_their_hostname_and_variables(parse):
    inventory, warnings = parse([vm(1, 'web.example.com', plan='KVM 2', state='running', cpus=2, memory=8192, disk=102400)])

    assert list(inventory.hosts) == ['web.example.com']
    assert inventory.get_host('web.example.com').vars == {
        'inventory_file': None,
        'inventory_dir': None,
        'ansible_host': '10.0.0.1',
        'plan': 'KVM 2',
        'state': 'running',
        'cpus': 2,
        'memory': 8192,
        'disk': 102400,
        'hostinger_id': 1,
    }
    assert warnings == []


def test_api_values_are_not_evaluated_as_templates(parse):
    inventory, warnings = parse([vm(1, "{{ 7 * 7 }}", plan="{{ 6 * 7 }}")])

    host = inventory.get_host('{{ 7 * 7 }}')
    templar = Templar(loader=DataLoader(), variables=dict(host.vars, inventory_hostname=host.name))
    assert templar.template(trust_as_template('{{ plan }}')) == '{{ 6 * 7 }}'
    assert templar.template(trust_as_template('{{ inventory_hostname }}')) == '{{ 7 * 7 }}'


@pytest.mark.parametrize('hostname', ['localhost', '127.0.0.1', '::1'])
def test_a_vm_cannot_claim_localhost(parse, hostname):
    inventory, warnings = parse([vm(7, hostname)])

    assert list(inventory.hosts) == ['srv7.hstgr.cloud']
    assert inventory.get_host('srv7.hstgr.cloud').vars['ansible_host'] == '10.0.0.7'
    assert warnings == [f"Hostinger VM 7 has hostname '{hostname}', which is local or shared by another VM; adding it as srv7.hstgr.cloud."]


def test_vms_sharing_a_hostname_each_get_their_own_host(parse):
    inventory, warnings = parse([vm(1, 'db.example.com'), vm(2, 'db.example.com'), vm(3, 'web.example.com')])

    assert list(inventory.hosts) == ['srv1.hstgr.cloud', 'srv2.hstgr.cloud', 'web.example.com']
    assert len(warnings) == 2


def test_a_vm_without_hostname_uses_its_default_hostname(parse):
    inventory, warnings = parse([vm(5, None), {'hostname': ''}, 'not a vm'])

    assert list(inventory.hosts) == ['srv5.hstgr.cloud', 'srvunknown.hstgr.cloud']
    assert warnings == []


def test_a_vm_whose_host_name_is_already_taken_is_skipped(parse):
    inventory, warnings = parse([vm(1, 'srv2.hstgr.cloud'), vm(2, 'localhost')])

    assert list(inventory.hosts) == ['srv2.hstgr.cloud']
    assert inventory.get_host('srv2.hstgr.cloud').vars['hostinger_id'] == 1
    assert warnings[-1] == 'Skipping Hostinger VM 2: the inventory already has a host named srv2.hstgr.cloud.'


def test_a_vm_without_ipv4_has_no_ansible_host(parse):
    inventory, warnings = parse([{'id': 1, 'hostname': 'web.example.com', 'ipv4': []}])

    assert 'ansible_host' not in inventory.get_host('web.example.com').vars


def test_api_errors_fail_the_inventory(parse):
    with pytest.raises(AnsibleError, match='Failed to fetch virtual machines from the Hostinger API: boom'):
        parse(HostingerApiError('boom'))


def test_a_response_that_is_not_a_list_fails_the_inventory(parse):
    with pytest.raises(AnsibleError, match='Expected a list of VMs'):
        parse({'data': []})


@pytest.mark.parametrize('path, expected', [('hostinger.yml', True), ('hostinger.yaml', True), ('hostinger.ini', False)])
def test_only_yaml_files_are_accepted(tmp_path, path, expected):
    (tmp_path / path).write_text('plugin: hostinger.vps.inventory\n')

    assert InventoryModule().verify_file(str(tmp_path / path)) is expected
