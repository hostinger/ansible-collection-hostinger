#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_ssh_key_binding
short_description: Attach public SSH keys to a Hostinger VPS
description:
  - Attaches one or more public SSH keys to a specified virtual machine.
options:
  virtual_machine_id:
    description: The ID of the VPS to attach the key(s) to
    required: true
    type: str
  keys:
    description:
      - The actual public keys to attach to the VPS (e.g., ssh-ed25519 AAAAC3NzaC1... user@host)
      - Each key must be in valid OpenSSH format.
    required: true
    type: list
    elements: str
    version_added: 1.1.0
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Attach SSH key(s) to VPS
  hostinger.vps.hostinger_vps_ssh_key_binding:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    keys:
      - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA... user@host"
'''

RETURN = '''
result:
  description: All SSH keys now attached to the VPS.
  returned: always
  type: list
  elements: dict
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
        virtual_machine_id=dict(type='str', required=True),
        keys=dict(type='list', required=True, elements='str', no_log=False)
    )

    module = AnsibleModule(argument_spec=module_args)

    vm_id = module.params["virtual_machine_id"]

    try:
        client = client_from_module(module)
        result = client.post(
            f"/api/vps/v1/virtual-machines/{vm_id}/ssh-keys",
            body={"keys": module.params["keys"]},
        )
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Attaching SSH keys")

    module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
