#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hostinger_vps_catalog_info
short_description: List products in the Hostinger catalog
version_added: 1.1.0
description:
  - Lists the products that can be purchased, with their prices.
  - The C(id) of a price, for example C(hostingercom-vps-kvm2-usd-1m), is the I(item_id) used to purchase it.
options:
  category:
    description:
      - Only return products of this category, for example C(VPS), C(DOMAIN), C(EMAIL) or C(HOSTING).
      - When omitted, products of every category are returned.
    type: str
  name:
    description:
      - Only return products whose name matches. Use C(*) as a wildcard, for example C(KVM*).
    type: str
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: List VPS plans
  hostinger.vps.hostinger_vps_catalog_info:
    category: VPS
  register: result

- name: Find the item ID of KVM 2 billed monthly in USD
  ansible.builtin.set_fact:
    item_id: >-
      {{ (result.catalog_items | selectattr('name', 'equalto', 'KVM 2') | first).prices
         | selectattr('period', 'equalto', 1) | selectattr('period_unit', 'equalto', 'month')
         | selectattr('currency', 'equalto', 'USD') | map(attribute='id') | first }}
'''

RETURN = r'''
catalog_items:
  description: Products with their prices. Prices are in cents.
  returned: success
  type: list
  elements: dict
  sample:
    - id: hostingercom-vps-kvm1
      name: KVM 1
      category: VPS
      metadata: {}
      prices:
        - id: hostingercom-vps-kvm1-usd-1m
          name: KVM 1 (billed every month)
          currency: USD
          price: 1949
          first_period_price: 999
          period: 1
          period_unit: month
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
        category=dict(type='str'),
        name=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    query = {key: module.params[key] for key in ('category', 'name') if module.params[key]}

    try:
        catalog_items = client_from_module(module).get("/api/billing/v1/catalog", query=query)
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Fetching the catalog")

    module.exit_json(changed=False, catalog_items=catalog_items)


if __name__ == '__main__':
    main()
