#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_action_info
short_description: List actions of a Hostinger virtual machine
version_added: 1.1.0
description:
  - Lists the actions (start, recreate, backup, and so on) performed on a virtual machine, newest first, or returns a
    single action.
  - Modules that start an action can wait for it themselves with their I(wait) option.
options:
  virtual_machine_id:
    description: ID of the virtual machine.
    required: true
    type: int
  action_id:
    description:
      - ID of the action to return.
      - When omitted, every action of the virtual machine is returned, collected from all pages of results.
    type: int
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List the actions of a virtual machine
  hostinger.vps.hostinger_vps_action_info:
    virtual_machine_id: 123456
  register: result

- name: Get one action
  hostinger.vps.hostinger_vps_action_info:
    virtual_machine_id: 123456
    action_id: 8123712
  register: result
'''

RETURN = r'''
actions:
  description: Actions; a single-item list when I(action_id) is set.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 8123712
      name: ct_restart
      state: success
      created_at: "2025-02-27T11:54:00Z"
      updated_at: "2025-02-27T11:58:00Z"
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
        virtual_machine_id=dict(type='int', required=True),
        action_id=dict(type='int'),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    path = f"/api/vps/v1/virtual-machines/{module.params['virtual_machine_id']}/actions"
    action_id = module.params['action_id']

    try:
        client = client_from_module(module)
        if action_id:
            actions = [client.get(f"{path}/{action_id}")]
        else:
            actions = client.get_all_pages(path)
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching actions")

    module.exit_json(changed=False, actions=actions)


if __name__ == '__main__':
    main()
