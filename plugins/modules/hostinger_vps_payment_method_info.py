#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_payment_methods_info
short_description: Retrieve payment methods from Hostinger API
description:
  - Gets available billing payment methods linked to your Hostinger account.
options:
  token:
    description: Bearer token for Hostinger API access
    required: true
    type: str
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Get payment methods
  hostinger.vps.hostinger_vps_payment_methods_info:
    token: "{{ hostinger_token }}"
  register: payment_methods

- name: Print available payment method IDs
  debug:
    var: item.id
  loop: "{{ payment_methods.methods }}"
'''

RETURN = '''
methods:
  description: List of available payment methods
  returned: always
  type: list
'''
def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True)
    )

    module = AnsibleModule(argument_spec=module_args)
    token = module.params['token']

    url = "https://developers.hostinger.com/api/billing/v1/payment-methods"

    headers = get_headers(token)

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            module.exit_json(changed=False, methods=resp.json())
        else:
            module.fail_json(msg=f"Failed to retrieve payment methods. Status: {resp.status_code}. Response: {resp.text}")
    except Exception as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == "__main__":
    main()
