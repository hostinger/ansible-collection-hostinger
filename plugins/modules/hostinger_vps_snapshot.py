#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_snapshot
short_description: Manage Hostinger VPS snapshots
description:
  - Get, create, delete, or restore a VPS snapshot on Hostinger.
options:
  virtual_machine_id:
    description: ID of the VPS
    required: true
    type: str
  state:
    description:
      - Desired snapshot action.
      - C(get) fetches snapshot info. Use M(hostinger.vps.hostinger_vps_snapshot_info) instead; C(get) will be removed in version 2.0.0.
      - C(create) creates a new snapshot.
      - C(delete) deletes the snapshot.
      - C(restore) restores from snapshot.
    required: true
    choices: [get, create, delete, restore]
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
  - hostinger.vps.action_wait
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Create snapshot
  hostinger.vps.hostinger_vps_snapshot:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    state: create

- name: Get snapshot info
  hostinger.vps.hostinger_vps_snapshot:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    state: get

- name: Delete snapshot
  hostinger.vps.hostinger_vps_snapshot:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    state: delete

- name: Restore snapshot
  hostinger.vps.hostinger_vps_snapshot:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    state: restore
'''

RETURN = '''
snapshot:
  description: Snapshot operation result or info
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
        state=dict(type='str', required=True, choices=["get", "create", "delete", "restore"])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    vm_id = module.params['virtual_machine_id']
    state = module.params['state']

    base_url = f"/api/vps/v1/virtual-machines/{vm_id}/snapshot"

    try:
        client = client_from_module(module)
        if state == "get":
            json_out = client.get(base_url)
        elif state == "create":
            json_out = client.post(base_url)
        elif state == "delete":
            json_out = client.delete(base_url)
        else:
            json_out = client.post(base_url + "/restore")

        if state != "get":
            json_out = wait_for_action_if_requested(module, client, vm_id, json_out)
    except HostingerApiError as error:
        fail_on_api_error(module, error, f"Snapshot '{state}'")

    module.exit_json(changed=(state != "get"), snapshot=json_out)


if __name__ == "__main__":
    main()
