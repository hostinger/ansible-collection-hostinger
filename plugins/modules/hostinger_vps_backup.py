#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_backup
short_description: Manage VPS backups on Hostinger
description:
  - Get or restore backups for a Hostinger VPS.
options:
  virtual_machine_id:
    description: ID of the VPS
    required: true
    type: str
  state:
    description:
      - Desired operation.
      - C(get) to list available backups. Use M(hostinger.vps.hostinger_vps_backup_info) instead; C(get) will be removed in version 2.0.0.
      - C(delete) is no longer supported by the Hostinger API and always fails. It will be removed in version 2.0.0.
      - C(restore) to restore from a backup.
    required: true
    choices: [get, delete, restore]
    type: str
  backup_id:
    description: Required for restore operations.
    type: str
    required: false
extends_documentation_fragment:
  - hostinger.vps.api
  - hostinger.vps.action_wait
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: List backups
  hostinger.vps.hostinger_vps_backup:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    state: get

- name: Restore a backup
  hostinger.vps.hostinger_vps_backup:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    backup_id: "{{ backup_id }}"
    state: restore
'''

RETURN = '''
backup:
  description: Backup operation result or backup list
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    action_wait_argument_spec,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
    wait_for_action_if_requested,
)


def main():
    module_args = api_argument_spec()
    module_args.update(action_wait_argument_spec())
    module_args.update(
        virtual_machine_id=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=["get", "delete", "restore"]),
        backup_id=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args)

    vm_id = module.params["virtual_machine_id"]
    state = module.params["state"]
    backup_id = module.params.get("backup_id")

    if state == "delete":
        module.fail_json(msg="Deleting backups is no longer supported by the Hostinger API.")

    if state == "restore" and not backup_id:
        module.fail_json(msg="backup_id is required for restoring a backup.")

    try:
        client = client_from_module(module)
        if state == "get":
            data = client.get(f"/api/vps/v1/virtual-machines/{vm_id}/backups")
        else:
            data = client.post(f"/api/vps/v1/virtual-machines/{vm_id}/backups/{backup_id}/restore")
            data = wait_for_action_if_requested(module, client, vm_id, data)
    except HostingerApiError as error:
        fail_on_api_error(module, error, f"Backup '{state}'")

    module.exit_json(changed=(state != "get"), backup=data)


if __name__ == '__main__':
    main()
