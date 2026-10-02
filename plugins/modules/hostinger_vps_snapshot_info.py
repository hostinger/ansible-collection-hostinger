#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_snapshot_info
short_description: Get the snapshot of a Hostinger virtual machine
version_added: 1.1.0
description:
  - Returns the snapshot of a virtual machine. A virtual machine has at most one snapshot.
  - Create, delete or restore the snapshot with M(hostinger.vps.hostinger_vps_snapshot).
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
- name: Get the snapshot
  hostinger.vps.hostinger_vps_snapshot_info:
    virtual_machine_id: 123456
  register: result

- name: Show when the snapshot expires
  ansible.builtin.debug:
    msg: "Snapshot expires at {{ result.snapshot.expires_at }}"
  when: result.snapshot
'''

RETURN = r'''
snapshot:
  description: The snapshot, or C(null) when the virtual machine has none.
  returned: success
  type: dict
  sample:
    id: 325
    restore_time: 1800
    created_at: "2025-02-27T11:54:22Z"
    expires_at: "2025-03-19T11:54:22Z"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)


def has_snapshot(snapshot):
    """The API answers with a placeholder whose ID is 0, rather than an empty response, when there is no snapshot."""
    return bool(snapshot) and bool(snapshot.get("id"))


def main():
    module_args = api_argument_spec()
    module_args.update(
        virtual_machine_id=dict(type='int', required=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        snapshot = client_from_module(module).get(
            f"/api/vps/v1/virtual-machines/{module.params['virtual_machine_id']}/snapshot"
        )
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching snapshot")

    module.exit_json(changed=False, snapshot=snapshot if has_snapshot(snapshot) else None)


if __name__ == '__main__':
    main()
