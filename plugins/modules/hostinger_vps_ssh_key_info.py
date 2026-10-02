#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_ssh_key_info
short_description: List public SSH keys of a Hostinger account
version_added: 1.1.0
description:
  - Lists the public SSH keys stored in the Hostinger account, collected from all pages of results.
  - Attach keys to a virtual machine with M(hostinger.vps.hostinger_vps_ssh_key_binding).
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List SSH keys
  hostinger.vps.hostinger_vps_ssh_key_info:
  register: result

- name: Attach the key named "laptop" to a virtual machine
  hostinger.vps.hostinger_vps_ssh_key_binding:
    virtual_machine_id: 123456
    public_key_ids: "{{ result.ssh_keys | selectattr('name', 'equalto', 'laptop') | map(attribute='id') | list }}"
'''

RETURN = r'''
ssh_keys:
  description: Public SSH keys of the account.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 325
      name: laptop
      key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@laptop
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)


def main():
    module = AnsibleModule(argument_spec=api_argument_spec(), supports_check_mode=True)

    try:
        ssh_keys = client_from_module(module).get_all_pages("/api/vps/v1/public-keys")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching SSH keys")

    module.exit_json(changed=False, ssh_keys=ssh_keys)


if __name__ == '__main__':
    main()
