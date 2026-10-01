#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)

DOCUMENTATION = r"""
---
module: hostinger_vps_reinstall
short_description: Recreate the operating system of a Hostinger VPS
description:
  - Recreates the OS on a Hostinger VPS using the specified template and optional post-install script.
  - This operation is irreversible and deletes all data and snapshots of the virtual machine.
version_added: "1.0.0"
author: "Hostinger Dev Team (@hostinger)"
options:
  virtual_machine_id:
    description: ID of the virtual machine to recreate.
    required: true
    type: str
  template_id:
    description: ID of the template to recreate the VPS with.
    required: true
    type: int
  password:
    description:
      - Root password for the recreated virtual machine.
      - Must be at least 12 characters long, contain an uppercase letter, a lowercase letter and a number, and must not
        appear in public password leaks.
    required: false
    type: str
    version_added: 1.1.0
  panel_password:
    description:
      - Panel password for templates that include a control panel.
      - Same requirements as I(password).
    required: false
    type: str
    version_added: 1.1.0
  public_ssh_key_id:
    description:
      - No longer supported by the Hostinger API; setting it fails.
      - Attach keys with M(hostinger.vps.hostinger_vps_ssh_key_binding) once the recreate has finished.
      - Will be removed in version 2.0.0.
    required: false
    type: str
  post_install_script_id:
    description: ID of the post-install script to run after recreate.
    required: false
    type: int
extends_documentation_fragment:
  - hostinger.vps.api
"""

EXAMPLES = r"""
- name: Recreate a VPS with a template and post-install script
  hostinger.vps.hostinger_vps_reinstall:
    token: "{{ hostinger_api_token }}"
    virtual_machine_id: "123456"
    template_id: 1002
    password: "{{ vps_root_password }}"
    post_install_script_id: 145
"""

RETURN = r"""
msg:
  description: Result message
  type: str
  returned: always
action:
  description: Action created for the recreate, which can be used to track its progress.
  type: dict
  returned: success
  version_added: 1.1.0
"""


def build_recreate_payload(params):
    payload = {"template_id": params["template_id"]}

    for option in ("password", "panel_password", "post_install_script_id"):
        if params.get(option) is not None:
            payload[option] = params[option]

    return payload


def main():
    module_args = api_argument_spec()
    module_args.update(
        virtual_machine_id=dict(type='str', required=True),
        template_id=dict(type='int', required=True),
        password=dict(type='str', required=False, no_log=True),
        panel_password=dict(type='str', required=False, no_log=True),
        public_ssh_key_id=dict(type='str', required=False, default=None),
        post_install_script_id=dict(type='int', required=False, default=None)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.params['public_ssh_key_id']:
        module.fail_json(
            msg="public_ssh_key_id is no longer supported by the Hostinger API. Remove it and attach the key with "
                "hostinger.vps.hostinger_vps_ssh_key_binding once the recreate has finished."
        )

    if module.check_mode:
        module.exit_json(changed=True, msg="Would recreate VPS in check mode.")

    vm_id = module.params['virtual_machine_id']

    try:
        action = client_from_module(module).post(
            f"/api/vps/v1/virtual-machines/{vm_id}/recreate",
            body=build_recreate_payload(module.params),
        )
    except HostingerApiError as error:
        fail_on_api_error(module, error, "VPS recreate")

    module.exit_json(changed=True, msg="VPS recreation triggered successfully.", action=action)


if __name__ == '__main__':
    main()
