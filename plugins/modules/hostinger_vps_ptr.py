#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_ptr
short_description: Set or delete PTR records on a Hostinger VPS
description:
  - Sets or deletes the PTR record (reverse DNS) of an IP address of a virtual machine.
options:
  virtual_machine_id:
    description: VPS ID
    required: true
    type: int
  ptr:
    description: PTR value to set (omit to delete)
    required: false
    type: str
  ip_address:
    description:
      - IP address of the virtual machine whose PTR record is set or deleted.
      - Defaults to the only IPv4 address of the virtual machine. Required when it has more than one.
    required: false
    type: str
    version_added: 1.1.0
extends_documentation_fragment:
  - hostinger.vps.api
  - hostinger.vps.action_wait
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Set PTR record
  hostinger.vps.hostinger_vps_ptr:
    token: "{{ hostinger_token }}"
    virtual_machine_id: 123456
    ptr: "custom.ptr.domain.com"

- name: Set PTR record of a specific IP address
  hostinger.vps.hostinger_vps_ptr:
    token: "{{ hostinger_token }}"
    virtual_machine_id: 123456
    ip_address: "203.0.113.10"
    ptr: "custom.ptr.domain.com"

- name: Delete PTR record
  hostinger.vps.hostinger_vps_ptr:
    token: "{{ hostinger_token }}"
    virtual_machine_id: 123456
'''

RETURN = '''
response:
  description: API response
  returned: success
  type: dict
'''

import ipaddress

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    action_wait_argument_spec,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
    wait_for_action_if_requested,
)


def same_ip_address(left, right):
    try:
        return ipaddress.ip_address(left) == ipaddress.ip_address(right)
    except ValueError:
        return left == right


def find_ip_address_id(virtual_machine, ip_address=None):
    """Return the API ID of an IP address of the virtual machine, which the PTR endpoints take instead of the address."""
    ipv4 = virtual_machine.get("ipv4") or []

    if ip_address:
        for entry in ipv4 + (virtual_machine.get("ipv6") or []):
            if same_ip_address(entry.get("address"), ip_address):
                return entry["id"]
        raise ValueError(f"IP address {ip_address} is not assigned to virtual machine {virtual_machine.get('id')}.")

    if len(ipv4) == 1:
        return ipv4[0]["id"]

    raise ValueError(
        f"Virtual machine {virtual_machine.get('id')} has {len(ipv4)} IPv4 addresses. Set ip_address to choose which one to update."
    )


def main():
    module_args = api_argument_spec()
    module_args.update(action_wait_argument_spec())
    module_args.update(
        virtual_machine_id=dict(type='int', required=True),
        ptr=dict(type='str', required=False),
        ip_address=dict(type='str', required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    vm_id = module.params["virtual_machine_id"]
    ptr = module.params.get("ptr")

    try:
        client = client_from_module(module)
        virtual_machine = client.get(f"/api/vps/v1/virtual-machines/{vm_id}")

        try:
            ip_address_id = find_ip_address_id(virtual_machine, module.params.get("ip_address"))
        except ValueError as error:
            module.fail_json(msg=str(error))

        url = f"/api/vps/v1/virtual-machines/{vm_id}/ptr/{ip_address_id}"
        if ptr:
            response = client.post(url, body={"domain": ptr})
        else:
            response = client.delete(url)
        response = wait_for_action_if_requested(module, client, vm_id, response)
    except HostingerApiError as error:
        fail_on_api_error(module, error, "PTR record update")

    module.exit_json(changed=True, response=response)


if __name__ == '__main__':
    main()
