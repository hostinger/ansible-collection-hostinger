#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_snapshot
short_description: Manage Hostinger VPS snapshots
description:
  - Get, create, delete, or restore a VPS snapshot on Hostinger.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
  virtual_machine_id:
    description: ID of the VPS
    required: true
    type: str
  state:
    description:
      - Desired snapshot action.
      - C(get) fetches snapshot info.
      - C(create) creates a new snapshot.
      - C(delete) deletes the snapshot.
      - C(restore) restores from snapshot.
    required: true
    choices: [get, create, delete, restore]
    type: str
author:
  - Hostinger Dev Team
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

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        virtual_machine_id=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=["get", "create", "delete", "restore"])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    token = module.params['token']
    vm_id = module.params['virtual_machine_id']
    state = module.params['state']

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    base_url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/snapshot"

    try:
        if state == "get":
            resp = requests.get(base_url, headers=headers)
        elif state == "create":
            resp = requests.post(base_url, headers=headers)
        elif state == "delete":
            resp = requests.delete(base_url, headers=headers)
        elif state == "restore":
            resp = requests.post(base_url + "/restore", headers=headers)
        else:
            module.fail_json(msg=f"Unknown state: {state}")

        if resp.status_code in [200, 201, 202, 204]:
            json_out = resp.json() if resp.content else {}
            module.exit_json(changed=(state != "get"), snapshot=json_out)
        else:
            module.fail_json(msg=f"Snapshot '{state}' failed. Status: {resp.status_code}. Response: {resp.text}")
    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == "__main__":
    main()
