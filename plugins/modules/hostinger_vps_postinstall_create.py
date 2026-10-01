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
module: hostinger_vps_postinstall_create
short_description: Create a post-install script on Hostinger VPS
description:
  - Creates a post-install script that can be used during VPS reinstallation.
version_added: "1.0.0"
author: "Hostinger Dev Team (@hostinger)"
options:
  name:
    description: Name for the post-install script.
    required: true
    type: str
  content:
    description: Shell script content to be executed after reinstall.
    required: true
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
"""

EXAMPLES = r"""
- name: Create a post-install script
  hostinger.vps.hostinger_vps_postinstall_create:
    token: "{{ hostinger_api_token }}"
    name: "Install Docker"
    content: |
      #!/bin/bash
      apt update && apt install -y docker.io
"""

RETURN = r"""
msg:
  description: Result message
  type: str
  returned: always
  sample: Post-install script created successfully.
script:
  description: Created script details
  type: dict
  returned: on success
"""


def main():
    module_args = api_argument_spec()
    module_args.update(
        name=dict(type='str', required=True),
        content=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(changed=True, msg="Would create post-install script in check mode.")

    payload = {
        "name": module.params['name'],
        "content": module.params['content']
    }

    try:
        script = client_from_module(module).post("/api/vps/v1/post-install-scripts", body=payload)
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Creating post-install script")

    module.exit_json(changed=True, msg="Post-install script created successfully.", script=script)


if __name__ == '__main__':
    main()
