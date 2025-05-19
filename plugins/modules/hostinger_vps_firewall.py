#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_firewall
short_description: Manage Hostinger VPS firewalls
description:
  - Create, get, or delete firewall configurations for Hostinger VPS.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
  state:
    description:
      - The desired state of the firewall.
    required: true
    type: str
    choices: [get, create, delete]
  firewall_id:
    description: Firewall ID (required for get/delete)
    required: false
    type: str
  name:
    description: Name of the firewall (required for create)
    required: false
    type: str
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Create a firewall
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: create
    name: "Allow SSH Only"

- name: Get all firewalls
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: get

- name: Get a firewall by ID
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: get
    firewall_id: "72122"

- name: Delete a firewall
  hostinger.vps.hostinger_vps_firewall:
    token: "{{ hostinger_token }}"
    state: delete
    firewall_id: "72122"
'''

RETURN = '''
firewall:
  description: Firewall result or list
  returned: always
  type: dict
'''

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', required=True, choices=['get', 'create', 'delete']),
        firewall_id=dict(type='str', required=False),
        name=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args)
    token = module.params['token']
    state = module.params['state']
    firewall_id = module.params.get('firewall_id')
    name = module.params.get('name')

    headers = get_headers(token)

    try:
        if state == 'get':
            if firewall_id:
                url = f"https://developers.hostinger.com/api/vps/v1/firewall/{firewall_id}"
            else:
                url = "https://developers.hostinger.com/api/vps/v1/firewall"
            resp = requests.get(url, headers=headers)

        elif state == 'create':
            if not name:
                module.fail_json(msg="Firewall name is required for creation.")
            url = "https://developers.hostinger.com/api/vps/v1/firewall"
            body = { "name": name }
            resp = requests.post(url, headers=headers, json=body)

        elif state == 'delete':
            if not firewall_id:
                module.fail_json(msg="firewall_id is required for deletion.")
            url = f"https://developers.hostinger.com/api/vps/v1/firewall/{firewall_id}"
            resp = requests.delete(url, headers=headers)

        else:
            module.fail_json(msg="Invalid state.")

        if resp.status_code in [200, 201, 202, 204]:
            output = resp.json() if resp.content else {}
            module.exit_json(changed=(state != 'get'), firewall=output)
        else:
            module.fail_json(msg=f"Firewall {state} failed. Status: {resp.status_code}. Response: {resp.text}")

    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == "__main__":
    main()
