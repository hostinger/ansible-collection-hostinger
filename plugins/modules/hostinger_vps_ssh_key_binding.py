#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_ssh_key_binding
short_description: Attach public SSH keys to a Hostinger VPS
description:
  - Attaches one or more existing public SSH keys to a specified virtual machine.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
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
author:
  - Hostinger Dev Team
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

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        virtual_machine_id=dict(type='str', required=True),
        public_key_ids=dict(type='list', required=True, elements='int')
    )

    module = AnsibleModule(argument_spec=module_args)

    token = module.params["token"]
    vm_id = module.params["virtual_machine_id"]
    key_ids = module.params["public_key_ids"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"https://developers.hostinger.com/api/vps/v1/public-keys/attach/{vm_id}"
    payload = { "ids": key_ids }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201, 202, 204]:
            result = response.json() if response.content else {}
            module.exit_json(changed=True, result=result)
        else:
            module.fail_json(msg=f"Failed to attach SSH keys. Status: {response.status_code}. Response: {response.text}")
    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == '__main__':
    main()
