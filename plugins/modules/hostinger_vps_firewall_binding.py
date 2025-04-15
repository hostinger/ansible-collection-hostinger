#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_firewall_binding
short_description: Activate, deactivate, or sync firewalls on Hostinger VPS
description:
  - Binds a firewall to a VPS (activate), removes it (deactivate), or syncs rules (sync).
options:
  token:
    description: Hostinger API token
    required: true
    type: str
  firewall_id:
    description: Firewall ID
    required: true
    type: str
  virtual_machine_id:
    description: Virtual Machine ID
    required: true
    type: str
  state:
    description:
      - Action to perform on the binding.
    required: true
    choices: [activate, deactivate, sync]
    type: str
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Activate firewall on VPS
  hostinger.vps.hostinger_vps_firewall_binding:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    virtual_machine_id: "{{ vm_id }}"
    state: activate

- name: Deactivate firewall
  hostinger.vps.hostinger_vps_firewall_binding:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    virtual_machine_id: "{{ vm_id }}"
    state: deactivate

- name: Sync firewall rules to VPS
  hostinger.vps.hostinger_vps_firewall_binding:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    virtual_machine_id: "{{ vm_id }}"
    state: sync
'''

RETURN = '''
result:
  description: Response from Hostinger API
  type: dict
  returned: always
'''

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        firewall_id=dict(type='str', required=True),
        virtual_machine_id=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=["activate", "deactivate", "sync"])
    )

    module = AnsibleModule(argument_spec=module_args)

    token = module.params["token"]
    firewall_id = module.params["firewall_id"]
    vm_id = module.params["virtual_machine_id"]
    state = module.params["state"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"https://developers.hostinger.com/api/vps/v1/firewall/{firewall_id}/{state}/{vm_id}"

    try:
        response = requests.post(url, headers=headers)

        if response.status_code in [200, 201, 202, 204]:
            result = response.json() if response.content else {}
            module.exit_json(changed=True, result=result)
        else:
            module.fail_json(msg=f"Firewall '{state}' failed. Status: {response.status_code}. Response: {response.text}")
    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == "__main__":
    main()
