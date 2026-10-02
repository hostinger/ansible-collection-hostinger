#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_post_install_script_info
short_description: List post-install scripts of a Hostinger account
version_added: 1.1.0
description:
  - Lists the post-install scripts of the Hostinger account, or returns a single one.
options:
  post_install_script_id:
    description:
      - ID of the post-install script to return.
      - When omitted, every script is returned, collected from all pages of results.
    type: int
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List post-install scripts
  hostinger.vps.hostinger_vps_post_install_script_info:
  register: result

- name: Get one post-install script
  hostinger.vps.hostinger_vps_post_install_script_info:
    post_install_script_id: 325
  register: result
'''

RETURN = r'''
post_install_scripts:
  description: Post-install scripts; a single-item list when I(post_install_script_id) is set.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 325
      name: Install nginx
      content: "#!/bin/bash\napt-get update\napt-get install -y nginx"
      created_at: "2025-02-27T11:54:22Z"
      updated_at: "2025-03-19T11:54:22Z"
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
        post_install_script_id=dict(type='int'),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    script_id = module.params['post_install_script_id']

    try:
        client = client_from_module(module)
        if script_id:
            scripts = [client.get(f"/api/vps/v1/post-install-scripts/{script_id}")]
        else:
            scripts = client.get_all_pages("/api/vps/v1/post-install-scripts")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching post-install scripts")

    module.exit_json(changed=False, post_install_scripts=scripts)


if __name__ == '__main__':
    main()
