#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_hostname
short_description: Set or reset the hostname of a Hostinger VPS
description:
  - Sets a custom hostname or resets it to the default along with the PTR record.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
  virtual_machine_id:
    description: ID of the VPS
    required: true
    type: int
  hostname:
    description: New hostname to set (omit to reset)
    required: false
    type: str
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Set hostname
  hostinger.vps.hostinger_vps_hostname:
    token: "{{ hostinger_token }}"
    virtual_machine_id: 123456
    hostname: "custom.hostinger.test"

- name: Reset hostname and PTR
  hostinger.vps.hostinger_vps_hostname:
    token: "{{ hostinger_token }}"
    virtual_machine_id: 123456
'''

RETURN = '''
response:
  description: API response
  type: dict
'''

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        virtual_machine_id=dict(type='int', required=True),
        hostname=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    token = module.params["token"]
    vm_id = module.params["virtual_machine_id"]
    hostname = module.params.get("hostname")

    headers = get_headers(token)

    try:
        if hostname:
            url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/hostname"
            payload = {"hostname": hostname}
            response = requests.put(url, json=payload, headers=headers)
        else:
            url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/hostname"
            response = requests.delete(url, headers=headers)

        response.raise_for_status()
        module.exit_json(changed=True, response=response.json())

    except requests.exceptions.RequestException as e:
        module.fail_json(msg=f"API request failed: {e}")

if __name__ == '__main__':
    main()
