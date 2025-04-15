#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_subscription_info
short_description: Get subscription details from Hostinger billing API
description:
  - Retrieves a list of subscriptions associated with the Hostinger API token.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Fetch all subscriptions
  hostinger.vps.hostinger_vps_subscription_info:
    token: "{{ hostinger_token }}"
'''

RETURN = '''
subscriptions:
  description: List of subscription objects
  returned: always
  type: list
'''

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
    )

    module = AnsibleModule(argument_spec=module_args)
    token = module.params["token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://developers.hostinger.com/api/billing/v1/subscriptions"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            module.exit_json(changed=False, subscriptions=data)
        else:
            module.fail_json(msg=f"Failed to fetch subscriptions. Status: {response.status_code}. Response: {response.text}")
    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == '__main__':
    main()
