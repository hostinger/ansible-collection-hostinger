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

DOCUMENTATION = r'''
---
module: hostinger_vps_provision
short_description: Automate Hostinger VPS provisioning
version_added: "1.0.0"
description:
  - Creates a new Hostinger VPS by first creating an order, then setting up the new virtual machine.
options:
  payment_method_id:
    description: ID of the payment method.
    required: true
    type: int
  item_id:
    description: VPS item ID (e.g. hostingercom-vps-kvm2-usd-1m).
    required: true
    type: str
  template_id:
    description: Template ID for the VPS OS.
    required: true
    type: int
  data_center_id:
    description: Data center ID to deploy the VPS.
    required: true
    type: int
  password:
    description: Root password for the VPS.
    required: true
    type: str
  hostname:
    description: Optional hostname. If not provided, a default will be assigned.
    required: false
    type: str
  coupons:
    description: Optional list of coupon codes.
    required: false
    type: list
    elements: str
    default: []
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
'''

EXAMPLES = r'''
- name: Provision a Hostinger VPS
  hostinger.vps.hostinger_vps_provision:
    token: "{{ hostinger_token }}"
    payment_method_id: 123456
    item_id: "hostingercom-vps-kvm2-usd-1m"
    template_id: 1002
    data_center_id: 13
    password: "Super.Strong1Pass456"
'''

RETURN = r'''
vps_details:
  description: JSON response of the provisioned VPS.
  type: dict
  returned: always
'''


def main():
    module_args = api_argument_spec()
    module_args.update(
        payment_method_id=dict(type="int", required=True),
        item_id=dict(type="str", required=True),
        template_id=dict(type="int", required=True),
        data_center_id=dict(type="int", required=True),
        password=dict(type="str", required=True, no_log=True),
        hostname=dict(type="str", required=False),
        coupons=dict(type="list", elements="str", required=False, default=[]),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    hostname = module.params.get("hostname")

    try:
        client = client_from_module(module)

        # Step 1: Create Order
        order_data = client.post("/api/billing/v1/orders", body={
            "payment_method_id": module.params["payment_method_id"],
            "items": [{"item_id": module.params["item_id"], "quantity": 1}],
            "coupons": module.params["coupons"],
        })
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Order creation")

    subscription_id = order_data.get("subscription_id") or order_data.get("subscription_ids", [None])[0]
    if not subscription_id:
        module.fail_json(msg="No subscription_id found in order response.", response=order_data)

    # Step 2: Find Matching VM
    try:
        vms = client.get("/api/vps/v1/virtual-machines")
    except HostingerApiError as error:
        fail_on_api_error(module, error, "Retrieving VMs")

    vm = next((vm for vm in vms if vm.get("subscription_id") == subscription_id), None)
    if not vm:
        module.fail_json(msg="No VM found with matching subscription ID.", subscription_id=subscription_id)

    vm_id = vm.get("id")
    if not vm_id:
        module.fail_json(msg="VM ID missing from matched virtual machine.", vm=vm)

    # Step 3: Setup VM
    setup_payload = {
        "template_id": module.params["template_id"],
        "data_center_id": module.params["data_center_id"],
        "password": module.params["password"],
    }
    if hostname is not None:
        setup_payload["hostname"] = hostname

    try:
        vps_details = client.post(f"/api/vps/v1/virtual-machines/{vm_id}/setup", body=setup_payload)
    except HostingerApiError as error:
        fail_on_api_error(module, error, "VPS setup")

    module.exit_json(changed=True, vps_details=vps_details)


if __name__ == '__main__':
    main()
