#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_backup
short_description: Manage VPS backups on Hostinger
description:
  - Get, delete, or restore backups for a Hostinger VPS.
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
      - Desired operation.
      - C(get) to list available backups.
      - C(delete) to delete a backup.
      - C(restore) to restore from a backup.
    required: true
    choices: [get, delete, restore]
    type: str
  backup_id:
    description: Required for delete/restore operations.
    type: str
    required: false
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: List backups
  hostinger.vps.hostinger_vps_backup:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    state: get

- name: Delete a backup
  hostinger.vps.hostinger_vps_backup:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    backup_id: "{{ backup_id }}"
    state: delete

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

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        virtual_machine_id=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=["get", "delete", "restore"]),
        backup_id=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args)

    token = module.params["token"]
    vm_id = module.params["virtual_machine_id"]
    state = module.params["state"]
    backup_id = module.params.get("backup_id")

    headers = get_headers(token)

    try:
        if state == "get":
            url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/backups"
            response = requests.get(url, headers=headers)

        elif state == "delete":
            if not backup_id:
                module.fail_json(msg="backup_id is required for deleting a backup.")
            url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/backups/{backup_id}"
            response = requests.delete(url, headers=headers)

        elif state == "restore":
            if not backup_id:
                module.fail_json(msg="backup_id is required for restoring a backup.")
            url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/backups/{backup_id}/restore"
            response = requests.post(url, headers=headers)

        else:
            module.fail_json(msg="Invalid state provided.")

        if response.status_code in [200, 201, 202, 204]:
            data = response.json() if response.content else {}
            module.exit_json(changed=(state != "get"), backup=data)
        else:
            module.fail_json(msg=f"Backup '{state}' failed. Status: {response.status_code}. Response: {response.text}")

    except requests.exceptions.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == '__main__':
    main()
