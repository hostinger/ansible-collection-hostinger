#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_payment_method_info
short_description: Retrieve payment methods from Hostinger API
description:
  - Gets available billing payment methods linked to your Hostinger account.
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Get payment methods
  hostinger.vps.hostinger_vps_payment_method_info:
    token: "{{ hostinger_token }}"
  register: payment_methods

- name: Print available payment method IDs
  debug:
    var: item.id
  loop: "{{ payment_methods.methods }}"
'''

RETURN = '''
methods:
  description: List of available payment methods
  returned: always
  type: list
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
        methods = client_from_module(module).get("/api/billing/v1/payment-methods")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Retrieving payment methods")

    module.exit_json(changed=False, methods=methods)


if __name__ == "__main__":
    main()
