#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = r"""
---
module: hostinger_vps_postinstall_list
short_description: List all post-install scripts on Hostinger VPS
description:
  - Retrieves a list of all post-install scripts available in the Hostinger VPS environment.
version_added: "1.0.0"
author: "Hostinger Dev Team"
options:
  token:
    description: Bearer token for Hostinger API authentication.
    required: true
    type: str
    no_log: true
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
  description: List of post-install scripts
  type: list
  returned: on success
  sample: [{"id": "abc123", "name": "Install Docker", "script": "#!/bin/bash ..."}]
"""

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    headers = {
        "Authorization": f"Bearer {module.params['token']}",
        "Content-Type": "application/json"
    }

    url = "https://developers.hostinger.com/api/vps/v1/post-install-scripts"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        module.exit_json(changed=False, scripts=response.json())
    else:
        module.fail_json(msg=f"Failed to retrieve scripts: {response.status_code} - {response.text}")

if __name__ == '__main__':
    main()
