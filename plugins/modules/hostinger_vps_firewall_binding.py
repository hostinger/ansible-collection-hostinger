#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)

DOCUMENTATION = '''
---
module: hostinger_vps_firewall_binding
short_description: Activate, deactivate, or sync firewalls on Hostinger VPS
description:
  - Binds a firewall to a VPS (activate), removes it (deactivate), or syncs rules (sync).
options:
  firewall_id:
    description: Firewall ID
    required: true
    type: str
  virtual_machine_id:
    description: Virtual Machine ID
    required: true
    type: str
  state:
    description:
      - Action to perform on the binding.
    required: true
    choices: [activate, deactivate, sync]
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Activate firewall on VPS
  hostinger.vps.hostinger_vps_firewall_binding:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    virtual_machine_id: "{{ vm_id }}"
    state: activate

- name: Deactivate firewall
  hostinger.vps.hostinger_vps_firewall_binding:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    virtual_machine_id: "{{ vm_id }}"
    state: deactivate

- name: Sync firewall rules to VPS
  hostinger.vps.hostinger_vps_firewall_binding:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    virtual_machine_id: "{{ vm_id }}"
    state: sync
'''

RETURN = '''
result:
  description: Response from Hostinger API
  type: dict
  returned: always
'''


def main():
    module_args = api_argument_spec()
    module_args.update(
        firewall_id=dict(type='str', required=True),
        virtual_machine_id=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=["activate", "deactivate", "sync"])
    )

    module = AnsibleModule(argument_spec=module_args)

    firewall_id = module.params["firewall_id"]
    vm_id = module.params["virtual_machine_id"]
    state = module.params["state"]

    try:
        result = client_from_module(module).post(f"/api/vps/v1/firewall/{firewall_id}/{state}/{vm_id}")
    except HostingerApiError as error:
        fail_on_api_error(module, error, f"Firewall '{state}'")

    module.exit_json(changed=True, result=result)


if __name__ == "__main__":
    main()
