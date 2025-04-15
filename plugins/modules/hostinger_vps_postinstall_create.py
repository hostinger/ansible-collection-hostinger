#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = r"""
---
module: hostinger_vps_postinstall_create
short_description: Create a post-install script on Hostinger VPS
description:
  - Creates a post-install script that can be used during VPS reinstallation.
version_added: "1.0.0"
author: "Hostinger Dev Team"
options:
  token:
    description: Bearer token for Hostinger API authentication.
    required: true
    type: str
    no_log: true
  name:
    description: Name for the post-install script.
    required: true
    type: str
  content:
    description: Shell script content to be executed after reinstall.
    required: true
    type: str
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
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        name=dict(type='str', required=True),
        content=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(changed=True, msg="Would create post-install script in check mode.")

    headers = {
        "Authorization": f"Bearer {module.params['token']}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": module.params['name'],
        "content": module.params['content']
    }

    url = "https://developers.hostinger.com/api/vps/v1/post-install-scripts"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        module.exit_json(changed=True, msg="Post-install script created successfully.", script=response.json())
    else:
        module.fail_json(msg=f"Failed to create post-install script: {response.status_code} - {response.text}")

if __name__ == '__main__':
    main()
