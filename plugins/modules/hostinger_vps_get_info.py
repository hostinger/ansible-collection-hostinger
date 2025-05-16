#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_get_info
short_description: Get details of a Hostinger VPS
description:
    - Retrieves detailed information about a specific Hostinger VPS.
options:
    token:
        description: API token for Hostinger
        required: true
        type: str
    virtual_machine_id:
        description: ID of the virtual machine to retrieve
        required: true
        type: str
author:
    - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Get VPS information
  hostinger.vps.hostinger_vps_get_info:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
'''

RETURN = '''
vps:
    description: VPS details from the Hostinger API
    returned: success
    type: dict
'''

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        virtual_machine_id=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    token = module.params["token"]
    
    headers = get_headers(token)

    url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{module.params['virtual_machine_id']}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            module.exit_json(changed=False, vps=response.json())
        else:
            module.fail_json(msg=f"Failed to fetch VPS info. Status: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == '__main__':
    main()
