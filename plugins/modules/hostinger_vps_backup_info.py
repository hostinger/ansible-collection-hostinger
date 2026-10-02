#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_backup_info
short_description: List backups of a Hostinger virtual machine
version_added: 1.1.0
description:
  - Lists the backups of a virtual machine, collected from all pages of results.
  - Restore a backup with M(hostinger.vps.hostinger_vps_backup).
options:
  virtual_machine_id:
    description: ID of the virtual machine.
    required: true
    type: int
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List backups
  hostinger.vps.hostinger_vps_backup_info:
    virtual_machine_id: 123456
  register: result

- name: Restore the newest backup
  hostinger.vps.hostinger_vps_backup:
    virtual_machine_id: 123456
    state: restore
    backup_id: "{{ (result.backups | sort(attribute='created_at') | last).id }}"
    wait: true
'''

RETURN = r'''
backups:
  description: Backups of the virtual machine.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 325
      location: nl-srv-nodebackups
      size: 15240192
      restore_time: 3600
      created_at: "2025-02-27T11:54:22Z"
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
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        backups = client_from_module(module).get_all_pages(
            f"/api/vps/v1/virtual-machines/{module.params['virtual_machine_id']}/backups"
        )
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching backups")

    module.exit_json(changed=False, backups=backups)


if __name__ == '__main__':
    main()
