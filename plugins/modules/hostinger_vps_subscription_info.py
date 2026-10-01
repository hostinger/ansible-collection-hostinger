#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_subscription_info
short_description: Get subscription details from Hostinger billing API
description:
  - Retrieves a list of subscriptions associated with the Hostinger API token.
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = '''
- name: Fetch all subscriptions
  hostinger.vps.hostinger_vps_subscription_info:
    token: "{{ hostinger_token }}"
'''

RETURN = '''
subscriptions:
  description: List of subscription objects
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
        subscriptions = client_from_module(module).get("/api/billing/v1/subscriptions")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching subscriptions")

    module.exit_json(changed=False, subscriptions=subscriptions)


if __name__ == '__main__':
    main()
