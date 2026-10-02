#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_template_info
short_description: List Hostinger VPS OS templates
version_added: 1.1.0
description:
  - Lists the OS templates a virtual machine can be set up or recreated with, or returns a single one.
options:
  template_id:
    description:
      - ID of the template to return.
      - When omitted, every template is returned.
    type: int
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List templates
  hostinger.vps.hostinger_vps_template_info:
  register: result

- name: Find the ID of the plain Ubuntu 24.04 template
  ansible.builtin.set_fact:
    template_id: "{{ (result.templates | selectattr('name', 'equalto', 'Ubuntu 24.04') | first).id }}"
'''

RETURN = r'''
templates:
  description: OS templates; a single-item list when I(template_id) is set.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 1210
      name: Ubuntu 24.04 with Docker and Traefik
      description: Docker is a modern containerization platform ...
      documentation: https://doc.traefik.io/traefik/
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
        template_id=dict(type='int'),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    template_id = module.params['template_id']

    try:
        client = client_from_module(module)
        if template_id:
            templates = [client.get(f"/api/vps/v1/templates/{template_id}")]
        else:
            templates = client.get("/api/vps/v1/templates")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching templates")

    module.exit_json(changed=False, templates=templates)


if __name__ == '__main__':
    main()
