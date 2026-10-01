#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_power
short_description: Start, stop, or restart a Hostinger VPS
description: >
  Perform power actions (start, stop, restart) on a Hostinger VPS instance using the Hostinger Public API.
options:
  virtual_machine_id:
    description:
      - The ID of the VPS instance to perform the action on.
    required: true
    type: str
  action:
    description:
      - The power action to perform on the VPS.
      - Valid options are C(start), C(stop), and C(restart).
    required: true
    type: str
    choices: [start, stop, restart]
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Start a Hostinger VPS
  hostinger.vps.hostinger_vps_power:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    action: start

- name: Restart a Hostinger VPS
  hostinger.vps.hostinger_vps_power:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    action: restart

- name: Stop a Hostinger VPS
  hostinger.vps.hostinger_vps_power:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    action: stop
'''

RETURN = '''
response:
  description: API response from Hostinger.
  type: dict
  returned: success
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
        action=dict(type='str', required=True, choices=['start', 'stop', 'restart'])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    vm_id = module.params['virtual_machine_id']
    action = module.params['action']

    if module.check_mode:
        module.exit_json(changed=False, msg=f"[CHECK_MODE] Would send {action} to VM {vm_id}")

    try:
        response = client_from_module(module).post(f"/api/vps/v1/virtual-machines/{vm_id}/{action}")
    except HostingerApiError as error:
        fail_on_api_error(module, error, f"Power action '{action}'")

    module.exit_json(changed=True, response=response)


if __name__ == '__main__':
    main()
