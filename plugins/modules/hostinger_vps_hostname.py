#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_hostname
short_description: Set or reset the hostname of a Hostinger VPS
description:
  - Sets a custom hostname or resets it to the default along with the PTR record.
options:
  virtual_machine_id:
    description: ID of the VPS
    required: true
    type: int
  hostname:
    description: New hostname to set (omit to reset)
    required: false
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
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
  returned: success
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
        virtual_machine_id=dict(type='int', required=True),
        hostname=dict(type='str', required=False)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    vm_id = module.params["virtual_machine_id"]
    hostname = module.params.get("hostname")
    url = f"/api/vps/v1/virtual-machines/{vm_id}/hostname"

    try:
        client = client_from_module(module)
        if hostname:
            response = client.put(url, body={"hostname": hostname})
        else:
            response = client.delete(url)
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Hostname update")

    module.exit_json(changed=True, response=response)


if __name__ == '__main__':
    main()
