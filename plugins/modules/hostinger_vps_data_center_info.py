#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_data_center_info
short_description: List Hostinger VPS data centers
version_added: 1.1.0
description:
  - Lists the data centers a new virtual machine can be set up in.
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List data centers
  hostinger.vps.hostinger_vps_data_center_info:
  register: result

- name: Find the ID of the Frankfurt data center
  ansible.builtin.set_fact:
    data_center_id: "{{ (result.data_centers | selectattr('city', 'equalto', 'Frankfurt') | first).id }}"
'''

RETURN = r'''
data_centers:
  description: Data centers.
  returned: success
  type: list
  elements: dict
  sample:
    - id: 19
      name: fra
      location: de
      city: Frankfurt
      continent: Europe
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)


def main():
    module = AnsibleModule(argument_spec=api_argument_spec(), supports_check_mode=True)

    try:
        data_centers = client_from_module(module).get("/api/vps/v1/data-centers")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching data centers")

    module.exit_json(changed=False, data_centers=data_centers)


if __name__ == '__main__':
    main()
