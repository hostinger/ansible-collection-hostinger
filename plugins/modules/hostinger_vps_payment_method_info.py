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


def main():
    module = AnsibleModule(argument_spec=api_argument_spec())

    try:
        methods = client_from_module(module).get("/api/billing/v1/payment-methods")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Retrieving payment methods")

    module.exit_json(changed=False, methods=methods)


if __name__ == "__main__":
    main()
