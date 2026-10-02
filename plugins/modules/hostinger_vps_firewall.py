#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_firewall
short_description: Manage Hostinger VPS firewalls
description:
  - Create, get, or delete firewall configurations for Hostinger VPS.
options:
  state:
    description:
      - The desired state of the firewall.
      - C(get) will be removed in version 2.0.0. Use M(hostinger.vps.hostinger_vps_firewall_info) instead.
    required: true
    type: str
    choices: [get, create, delete]
  firewall_id:
    description: Firewall ID (required for get/delete)
    required: false
    type: str
  name:
    description: Name of the firewall (required for create)
    required: false
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Create a firewall
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: create
    name: "Allow SSH Only"

- name: Get all firewalls
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: get

- name: Get a firewall by ID
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: get
    firewall_id: "72122"

- name: Delete a firewall
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: delete
    firewall_id: "72122"
'''

RETURN = '''
firewall:
  description: Firewall result or list
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)


def main():
    module_args = api_argument_spec()
    module_args.update(
        state=dict(type='str', required=True, choices=['get', 'create', 'delete']),
        firewall_id=dict(type='str', required=False),
        name=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args)
    state = module.params['state']
    firewall_id = module.params.get('firewall_id')
    name = module.params.get('name')

    if state == 'create' and not name:
        module.fail_json(msg="Firewall name is required for creation.")
    if state == 'delete' and not firewall_id:
        module.fail_json(msg="firewall_id is required for deletion.")

    try:
        client = client_from_module(module)
        if state == 'get':
            if firewall_id:
                output = client.get(f"/api/vps/v1/firewall/{firewall_id}")
            else:
                output = client.get("/api/vps/v1/firewall")
        elif state == 'create':
            output = client.post("/api/vps/v1/firewall", body={"name": name})
        else:
            output = client.delete(f"/api/vps/v1/firewall/{firewall_id}")
    except HostingerApiError as error:
        fail_on_api_error(module, error, f"Firewall {state}")

    module.exit_json(changed=(state != 'get'), firewall=output)


if __name__ == "__main__":
    main()
