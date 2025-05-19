#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = '''
---
module: hostinger_vps_metrics
short_description: Get performance metrics for a Hostinger VPS
description:
  - Retrieves resource usage metrics (CPU, memory, bandwidth, etc.) for a specific Hostinger virtual machine.
  - Requires a date range using ISO 8601 format for both start and end.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
  virtual_machine_id:
    description: ID of the VPS to retrieve metrics for
    required: true
    type: str
  date_from:
    description: ISO8601 start datetime (e.g., 2025-04-07T00:00:00Z)
    required: true
    type: str
  date_to:
    description: ISO8601 end datetime (e.g., 2025-04-08T00:00:00Z)
    required: true
    type: str
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Get VPS metrics
  hostinger.vps.hostinger_vps_metrics:
    token: "{{ hostinger_token }}"
    virtual_machine_id: "{{ vm_id }}"
    date_from: "2025-04-07T00:00:00Z"
    date_to: "2025-04-08T00:00:00Z"
'''

RETURN = '''
metrics:
  description: Metrics information returned from the Hostinger API
  returned: always
  type: dict
'''

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        virtual_machine_id=dict(type='str', required=True),
        date_from=dict(type='str', required=True),
        date_to=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    token = module.params["token"]
    
    headers = get_headers(token)

    vm_id = module.params["virtual_machine_id"]
    url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/metrics"

    params = {
        "date_from": module.params["date_from"],
        "date_to": module.params["date_to"]
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            module.exit_json(changed=False, metrics=response.json())
        else:
            module.fail_json(msg=f"Failed to fetch metrics. Status: {response.status_code}. Response: {response.text}")
    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == '__main__':
    main()
