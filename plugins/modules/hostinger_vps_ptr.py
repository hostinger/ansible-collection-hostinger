#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_ptr
short_description: Set or delete PTR records on a Hostinger VPS
description:
  - Sets or deletes PTR record (reverse DNS) on IPv4 of a virtual machine.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
  virtual_machine_id:
    description: VPS ID
    required: true
    type: int
  ptr:
    description: PTR value to set (omit to delete)
    required: false
    type: str
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Set PTR record
  hostinger.vps.hostinger_vps_ptr:
    token: "{{ hostinger_token }}"
    virtual_machine_id: 123456
    ptr: "custom.ptr.domain.com"

- name: Delete PTR record
  hostinger.vps.hostinger_vps_ptr:
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
        ptr=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    token = module.params["token"]
    vm_id = module.params["virtual_machine_id"]
    ptr = module.params.get("ptr")

    headers = get_headers(token)

    try:
        if ptr:
            url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/ptr"
            payload = {"ptr": ptr}
            response = requests.post(url, json=payload, headers=headers)
        else:
            url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/ptr"
            response = requests.delete(url, headers=headers)

        response.raise_for_status()
        module.exit_json(changed=True, response=response.json())

    except requests.exceptions.RequestException as e:
        module.fail_json(msg=f"API request failed: {e}")

if __name__ == '__main__':
    main()
