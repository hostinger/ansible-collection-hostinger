#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_get_info
short_description: Get details of a Hostinger VPS
description:
    - Retrieves detailed information about a specific Hostinger VPS.
options:
    virtual_machine_id:
        description: ID of the virtual machine to retrieve
        required: true
        type: str
extends_documentation_fragment:
    - hostinger.vps.api
author:
    - Hostinger Dev Team (@hostinger)
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
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        vps = client_from_module(module).get(f"/api/vps/v1/virtual-machines/{module.params['virtual_machine_id']}")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching VPS info")

    module.exit_json(changed=False, vps=vps)


if __name__ == '__main__':
    main()
