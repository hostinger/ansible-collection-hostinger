#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_ssh_key
short_description: Manage SSH keys for Hostinger VPS
description:
  - Create, list, or delete public SSH keys on your Hostinger account.
options:
  state:
    description:
      - The desired state of the SSH key.
    required: true
    choices: [get, create, delete]
    type: str
  public_key_id:
    description: ID of the key to delete
    required: false
    type: str
  name:
    description: Name of the SSH key (required for create)
    required: false
    type: str
  key:
    description:
      - The actual public key (e.g., ssh-ed25519 AAAAC3NzaC1... user@host)
      - Must be a valid OpenSSH format.
    required: false
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: List SSH keys
  hostinger.vps.hostinger_vps_ssh_key:
    token: "{{ hostinger_token }}"
    state: get

- name: Create SSH key
  hostinger.vps.hostinger_vps_ssh_key:
    token: "{{ hostinger_token }}"
    state: create
    name: MyLaptopKey
    key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA... user@host"

- name: Delete SSH key
  hostinger.vps.hostinger_vps_ssh_key:
    token: "{{ hostinger_token }}"
    state: delete
    public_key_id: "237652"
'''

RETURN = '''
ssh_key:
  description: SSH key result or list
  returned: always
  type: dict
'''

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)


def is_valid_ssh_key(key):
    """Basic OpenSSH format validator"""
    return re.match(r'^(ssh-(rsa|ed25519)|ecdsa-[a-zA-Z0-9-]+) [A-Za-z0-9+/=]+(?: [^\s]+)?$', key.strip()) is not None


def main():
    module_args = api_argument_spec()
    module_args.update(
        state=dict(type='str', required=True, choices=["get", "create", "delete"]),
        public_key_id=dict(type='str', required=False),
        name=dict(type='str', required=False),
        key=dict(type='str', required=False, no_log=False)
    )

    module = AnsibleModule(argument_spec=module_args)
    state = module.params['state']
    public_key_id = module.params.get('public_key_id')
    name = module.params.get('name')
    key = module.params.get('key')

    if state == 'create':
        if not name or not key:
            module.fail_json(msg="Both 'name' and 'key' are required for creating an SSH key.")
        if not is_valid_ssh_key(key):
            module.fail_json(msg="The SSH key is not valid OpenSSH format.")
    if state == 'delete' and not public_key_id:
        module.fail_json(msg="'public_key_id' is required for deleting an SSH key.")

    try:
        client = client_from_module(module)
        if state == 'get':
            result = client.get("/api/vps/v1/public-keys")
        elif state == 'create':
            result = client.post("/api/vps/v1/public-keys", body={"name": name, "key": key})
        else:
            result = client.delete(f"/api/vps/v1/public-keys/{public_key_id}")
    except HostingerApiError as error:
        fail_on_api_error(module, error, f"SSH key '{state}'")

    module.exit_json(changed=(state != "get"), ssh_key=result)


if __name__ == '__main__':
    main()
