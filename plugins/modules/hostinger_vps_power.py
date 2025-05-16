#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_power
short_description: Start, stop, or restart a Hostinger VPS
description: >
  Perform power actions (start, stop, restart) on a Hostinger VPS instance using the Hostinger Public API.
options:
  token:
    description:
      - The Hostinger API token used for authentication.
    required: true
    type: str
  virtual_machine_id:
    description:
      - The ID of the VPS instance to perform the action on.
    required: true
    type: str
  action:
    description:
      - The power action to perform on the VPS.
      - Valid options are C(start), C(stop), and C(restart).
    required: true
    type: str
    choices: [start, stop, restart]
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Start a Hostinger VPS
  hostinger.vps.hostinger_vps_power:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    action: start

- name: Restart a Hostinger VPS
  hostinger.vps.hostinger_vps_power:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    action: restart

- name: Stop a Hostinger VPS
  hostinger.vps.hostinger_vps_power:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    action: stop
'''

RETURN = '''
changed:
  description: Whether the VPS action caused a change.
  type: bool
  returned: always
response:
  description: API response from Hostinger.
  type: dict
  returned: success
'''

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        virtual_machine_id=dict(type='str', required=True),
        action=dict(type='str', required=True, choices=['start', 'stop', 'restart'])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    token = module.params['token']
    vm_id = module.params['virtual_machine_id']
    action = module.params['action']

    url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/{action}"
    headers = get_headers(token)

    if module.check_mode:
        module.exit_json(changed=False, msg=f"[CHECK_MODE] Would send {action} to VM {vm_id}")

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        json_data = response.json() if response.text else {}
        module.exit_json(changed=True, response=json_data)
    except requests.exceptions.HTTPError as err:
        module.fail_json(msg=f"Failed to perform action '{action}'. Status: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == '__main__':
    main()
