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
module: hostinger_vps_postinstall_delete
short_description: Delete a post-install script from Hostinger VPS
description:
  - Deletes a specific post-install script using its ID.
version_added: "1.0.0"
author: "Hostinger Dev Team (@hostinger)"
options:
  post_install_script_id:
    description: ID of the post-install script to delete.
    required: true
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
"""

EXAMPLES = r"""
- name: Delete a post-install script
  hostinger.vps.hostinger_vps_postinstall_delete:
    token: "{{ hostinger_api_token }}"
    post_install_script_id: "325"
"""

RETURN = r"""
msg:
  description: Result message
  type: str
  returned: always
"""


def main():
    module_args = api_argument_spec()
    module_args.update(
        post_install_script_id=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(changed=True, msg="Would delete post-install script in check mode.")

    script_id = module.params['post_install_script_id']

    try:
        client_from_module(module).delete(f"/api/vps/v1/post-install-scripts/{script_id}")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Deleting post-install script")

    module.exit_json(changed=True, msg="Post-install script deleted successfully.")


if __name__ == '__main__':
    main()
