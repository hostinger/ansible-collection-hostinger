#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: hostinger_vps_postinstall_list
short_description: List all post-install scripts on Hostinger VPS
description:
  - Retrieves a list of all post-install scripts available in the Hostinger VPS environment.
version_added: "1.0.0"
author: "Hostinger Dev Team (@hostinger)"
extends_documentation_fragment:
  - hostinger.vps.api
"""

EXAMPLES = r"""
- name: List all post-install scripts
  hostinger.vps.hostinger_vps_postinstall_list:
    token: "{{ hostinger_api_token }}"
  register: result

- debug:
    var: result.scripts
"""

RETURN = r"""
scripts:
  description: List of post-install scripts, collected from every page of results.
  type: list
  elements: dict
  returned: on success
  sample: [{"id": 325, "name": "Install Docker", "content": "#!/bin/bash ..."}]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)


def main():
    module = AnsibleModule(
        argument_spec=api_argument_spec(),
        supports_check_mode=True
    )

    try:
        scripts = client_from_module(module).get_all_pages("/api/vps/v1/post-install-scripts")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Listing post-install scripts")

    module.exit_json(changed=False, scripts=scripts)


if __name__ == '__main__':
    main()
