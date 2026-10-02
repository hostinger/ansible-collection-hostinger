#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_firewall_info
short_description: List Hostinger VPS firewalls
version_added: 1.1.0
description:
  - Lists the firewalls of the Hostinger account with their rules, or returns a single one.
options:
  firewall_id:
    description:
      - ID of the firewall to return.
      - When omitted, every firewall is returned, collected from all pages of results.
    type: int
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List firewalls
  hostinger.vps.hostinger_vps_firewall_info:
  register: result

- name: Get one firewall
  hostinger.vps.hostinger_vps_firewall_info:
    firewall_id: 72122
  register: result
'''

RETURN = r'''
firewalls:
  description: Firewalls; a single-item list when I(firewall_id) is set.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 72122
      name: Allow SSH only
      is_synced: true
      rules:
        - {id: 246950, action: accept, protocol: TCP, port: "22", source: any, source_detail: any}
      created_at: "2025-02-27T11:54:22Z"
      updated_at: "2025-02-27T11:54:22Z"
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
        firewall_id=dict(type='int'),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    firewall_id = module.params['firewall_id']

    try:
        client = client_from_module(module)
        if firewall_id:
            firewalls = [client.get(f"/api/vps/v1/firewall/{firewall_id}")]
        else:
            firewalls = client.get_all_pages("/api/vps/v1/firewall")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching firewalls")

    module.exit_json(changed=False, firewalls=firewalls)


if __name__ == '__main__':
    main()
