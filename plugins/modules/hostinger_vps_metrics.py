#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_metrics
short_description: Get performance metrics for a Hostinger VPS
description:
  - Retrieves resource usage metrics (CPU, memory, bandwidth, etc.) for a specific Hostinger virtual machine.
  - Requires a date range using ISO 8601 format for both start and end.
options:
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
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)


def main():
    module_args = api_argument_spec()
    module_args.update(
        virtual_machine_id=dict(type='str', required=True),
        date_from=dict(type='str', required=True),
        date_to=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    vm_id = module.params["virtual_machine_id"]
    query = {
        "date_from": module.params["date_from"],
        "date_to": module.params["date_to"]
    }

    try:
        metrics = client_from_module(module).get(f"/api/vps/v1/virtual-machines/{vm_id}/metrics", query=query)
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching metrics")

    module.exit_json(changed=False, metrics=metrics)


if __name__ == '__main__':
    main()
