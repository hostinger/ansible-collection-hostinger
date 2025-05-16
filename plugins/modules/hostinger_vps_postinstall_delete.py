#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = r"""
---
module: hostinger_vps_postinstall_delete
short_description: Delete a post-install script from Hostinger VPS
description:
  - Deletes a specific post-install script using its ID.
version_added: "1.0.0"
author: "Hostinger Dev Team"
options:
  token:
    description: Bearer token for Hostinger API authentication.
    required: true
    type: str
    no_log: true
  post_install_script_id:
    description: ID of the post-install script to delete.
    required: true
    type: str
"""

EXAMPLES = r"""
- name: Delete a post-install script
  hostinger.vps.hostinger_vps_postinstall_delete:
    token: "{{ hostinger_api_token }}"
    post_install_script_id: "script-123"
"""

RETURN = r"""
msg:
  description: Result message
  type: str
  returned: always
"""

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        post_install_script_id=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(changed=True, msg="Would delete post-install script in check mode.")

    token = module.params["token"]
    
    headers = get_headers(token)

    script_id = module.params['post_install_script_id']
    url = f"https://developers.hostinger.com/api/vps/v1/post-install-scripts/{script_id}"
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        module.exit_json(changed=True, msg="Post-install script deleted successfully.")
    else:
        module.fail_json(msg=f"Failed to delete script: {response.status_code} - {response.text}")

if __name__ == '__main__':
    main()
