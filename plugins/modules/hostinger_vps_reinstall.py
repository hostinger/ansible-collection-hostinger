#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = r"""
---
module: hostinger_vps_recreate
short_description: recreate the operating system of a Hostinger VPS
description:
  - recreates the OS on a Hostinger VPS using the specified template and optional SSH key and post-install script.
version_added: "1.0.0"
author: "Hostinger Dev Team"
options:
  token:
    description: Bearer token for Hostinger API authentication.
    required: true
    type: str
    no_log: true
  virtual_machine_id:
    description: ID of the virtual machine to recreate.
    required: true
    type: str
  template_id:
    description: ID of the template to recreate the VPS with.
    required: true
    type: str
  public_ssh_key_id:
    description: ID of the public SSH key to inject.
    required: false
    type: str
  post_install_script_id:
    description: ID of the post-install script to run after recreate.
    required: false
    type: str
"""

EXAMPLES = r"""
- name: recreate a VPS with Ubuntu template and SSH key
  hostinger.vps.hostinger_vps_recreate:
    token: "{{ hostinger_api_token }}"
    virtual_machine_id: "123456"
    template_id: "ubuntu-22-04"
    public_ssh_key_id: "sshkey-789"
    post_install_script_id: "145"
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
        virtual_machine_id=dict(type='str', required=True),
        template_id=dict(type='str', required=True),
        public_ssh_key_id=dict(type='str', required=False, default=None),
        post_install_script_id=dict(type='str', required=False, default=None)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    token = module.params['token']
    vm_id = module.params['virtual_machine_id']
    template_id = module.params['template_id']
    ssh_key = module.params['public_ssh_key_id']
    post_script = module.params['post_install_script_id']

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"https://developers.hostinger.com/api/vps/v1/virtual-machines/{vm_id}/recreate"

    if module.check_mode:
        module.exit_json(changed=True, msg="Would recreate VPS in check mode.")

    payload = {
        "templateId": template_id
    }

    if ssh_key:
        payload["publicSshKeyId"] = ssh_key
    if post_script:
        payload["postInstallScriptId"] = post_script

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 204:
        module.exit_json(changed=True, msg="VPS recreation triggered successfully.")
    else:
        module.fail_json(msg=f"Failed to recreate VPS. Status: {response.status_code}. Response: {response.text}")

if __name__ == '__main__':
    main()
