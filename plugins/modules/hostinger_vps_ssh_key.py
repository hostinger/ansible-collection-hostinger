#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests
import re

DOCUMENTATION = '''
---
module: hostinger_vps_ssh_key
short_description: Manage SSH keys for Hostinger VPS
description:
  - Create, list, or delete public SSH keys on your Hostinger account.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
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
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
# List SSH keys
ansible-playbook ssh_key_vps.yml --extra-vars '{"hostinger_token": "TOKEN", "ssh_key_action": "get"}'

# Create SSH key
ansible-playbook ssh_key_vps.yml --extra-vars '{
  "hostinger_token": "TOKEN",
  "ssh_key_action": "create",
  "ssh_key_name": "MyLaptopKey",
  "key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA... user@host"
}'

# Delete SSH key
ansible-playbook ssh_key_vps.yml --extra-vars '{
  "hostinger_token": "TOKEN",
  "ssh_key_action": "delete",
  "public_key_id": 237652
}'
'''

RETURN = '''
ssh_key:
  description: SSH key result or list
  returned: always
  type: dict
'''

def is_valid_ssh_key(key):
    """Basic OpenSSH format validator"""
    return re.match(r'^(ssh-(rsa|ed25519)|ecdsa-[a-zA-Z0-9-]+) [A-Za-z0-9+/=]+(?: [^\s]+)?$', key.strip()) is not None

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', required=True, choices=["get", "create", "delete"]),
        public_key_id=dict(type='str', required=False),
        name=dict(type='str', required=False),
        key=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args)
    token = module.params['token']
    state = module.params['state']
    public_key_id = module.params.get('public_key_id')
    name = module.params.get('name')
    key = module.params.get('key')

    headers = get_headers(token)

    try:
        if state == 'get':
            url = "https://developers.hostinger.com/api/vps/v1/public-keys"
            response = requests.get(url, headers=headers)

        elif state == 'create':
            if not name or not key:
                module.fail_json(msg="Both 'name' and 'key' are required for creating an SSH key.")
            if not is_valid_ssh_key(key):
                module.fail_json(msg="The SSH key is not valid OpenSSH format.")
            url = "https://developers.hostinger.com/api/vps/v1/public-keys"
            payload = {
                "name": name,
                "key": key
            }
            response = requests.post(url, headers=headers, json=payload)

        elif state == 'delete':
            if not public_key_id:
                module.fail_json(msg="'public_key_id' is required for deleting an SSH key.")
            url = f"https://developers.hostinger.com/api/vps/v1/public-keys/{public_key_id}"
            response = requests.delete(url, headers=headers)

        else:
            module.fail_json(msg="Invalid state provided.")

        if response.status_code in [200, 201, 202, 204]:
            result = response.json() if response.content else {}
            module.exit_json(changed=(state != "get"), ssh_key=result)
        else:
            module.fail_json(msg=f"SSH key '{state}' failed. Status: {response.status_code}. Response: {response.text}")

    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == '__main__':
    main()
