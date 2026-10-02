#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_vm_info
short_description: List Hostinger virtual machines
version_added: 1.1.0
description:
  - Lists the virtual machines of the Hostinger account, or returns a single one.
options:
  virtual_machine_id:
    description:
      - ID of the virtual machine to return.
      - When omitted, every virtual machine of the account is returned.
    type: int
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List all virtual machines
  hostinger.vps.hostinger_vps_vm_info:
  register: result

- name: Get one virtual machine
  hostinger.vps.hostinger_vps_vm_info:
    virtual_machine_id: 123456
  register: result

- name: Show the IPv4 address of every running virtual machine
  ansible.builtin.debug:
    msg: "{{ item.hostname }}: {{ item.ipv4[0].address }}"
  loop: "{{ result.virtual_machines | selectattr('state', 'equalto', 'running') }}"
'''

RETURN = r'''
virtual_machines:
  description: Virtual machines; a single-item list when I(virtual_machine_id) is set.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 123456
      hostname: srv123456.hstgr.cloud
      state: running
      actions_lock: unlocked
      plan: KVM 2
      cpus: 2
      memory: 8192
      disk: 102400
      data_center_id: 11
      firewall_group_id: null
      ipv4: [{id: 1536360, address: 203.0.113.10, ptr: srv123456.hstgr.cloud}]
      template: {id: 1210, name: Ubuntu 24.04 with Docker and Traefik}
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
        virtual_machine_id=dict(type='int'),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    vm_id = module.params['virtual_machine_id']

    try:
        client = client_from_module(module)
        if vm_id:
            virtual_machines = [client.get(f"/api/vps/v1/virtual-machines/{vm_id}")]
        else:
            virtual_machines = client.get("/api/vps/v1/virtual-machines")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching virtual machines")

    module.exit_json(changed=False, virtual_machines=virtual_machines)


if __name__ == '__main__':
    main()
