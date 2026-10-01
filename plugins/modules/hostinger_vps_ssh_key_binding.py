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
  - Attaches one or more existing public SSH keys to a specified virtual machine.
options:
  virtual_machine_id:
    description: The ID of the VPS to attach the key(s) to
    required: true
    type: str
  public_key_ids:
    description:
      - List of public SSH key IDs to attach to the VPS
    required: true
    type: list
    elements: int
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
    public_key_ids:
      - 237652
'''

RETURN = '''
result:
  description: API response
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
        virtual_machine_id=dict(type='str', required=True),
        public_key_ids=dict(type='list', required=True, elements='int')
    )

    module = AnsibleModule(argument_spec=module_args)

    vm_id = module.params["virtual_machine_id"]

    try:
        result = client_from_module(module).post(
            f"/api/vps/v1/public-keys/attach/{vm_id}",
            body={"ids": module.params["public_key_ids"]},
        )
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Attaching SSH keys")

    module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()
