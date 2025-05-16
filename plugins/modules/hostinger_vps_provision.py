# Ansible module to provision a Hostinger VPS via API
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests

DOCUMENTATION = r'''
---
module: hostinger_vps_provision
short_description: Automate Hostinger VPS provisioning
version_added: "1.0.0"
description:
  - Creates a new Hostinger VPS by first creating an order, then setting up the new virtual machine.
options:
  token:
    description: API token for Hostinger (Bearer token).
    required: true
    type: str
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
    module = AnsibleModule(
        argument_spec={
            "token": {"type": "str", "required": True, "no_log": True},
            "payment_method_id": {"type": "int", "required": True},
            "item_id": {"type": "str", "required": True},
            "template_id": {"type": "int", "required": True},
            "data_center_id": {"type": "int", "required": True},
            "password": {"type": "str", "required": True, "no_log": True},
            "hostname": {"type": "str", "required": False},
            "coupons": {"type": "list", "elements": "str", "required": False, "default": []},
        },
        supports_check_mode=False
    )

    token = module.params["token"]
    payment_method_id = module.params["payment_method_id"]
    item_id = module.params["item_id"]
    template_id = module.params["template_id"]
    data_center_id = module.params["data_center_id"]
    password = module.params["password"]
    hostname = module.params.get("hostname")
    coupons = module.params["coupons"]

    headers = get_headers(token)
    base_url = "https://developers.hostinger.com"

    # Step 1: Create Order
    order_payload = {
        "payment_method_id": payment_method_id,
        "items": [{"item_id": item_id, "quantity": 1}],
        "coupons": coupons
    }

    try:
        order_resp = requests.post(f"{base_url}/api/billing/v1/orders", headers=headers, json=order_payload)
        order_resp.raise_for_status()
        order_data = order_resp.json()
        subscription_id = order_data.get("subscription_id") or order_data.get("subscription_ids", [None])[0]
    except Exception as e:
        module.fail_json(msg=f"Order creation failed: {str(e)}")

    if not subscription_id:
        module.fail_json(msg="No subscription_id found in order response.", response=order_data)

    # Step 2: Find Matching VM
    try:
        vms_resp = requests.get(f"{base_url}/api/vps/v1/virtual-machines", headers=headers)
        vms_resp.raise_for_status()
        vms = vms_resp.json()
        vm = next((vm for vm in vms if vm.get("subscription_id") == subscription_id), None)
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve VMs: {str(e)}")

    if not vm:
        module.fail_json(msg="No VM found with matching subscription ID.", subscription_id=subscription_id)

    vm_id = vm.get("id")
    if not vm_id:
        module.fail_json(msg="VM ID missing from matched virtual machine.", vm=vm)

    # Step 3: Setup VM
    setup_payload = {
        "template_id": template_id,
        "data_center_id": data_center_id,
        "password": password
    }
    if hostname is not None:
        if not isinstance(hostname, str):
            module.fail_json(msg="The 'hostname' must be a string if provided.")
        setup_payload["hostname"] = hostname

    try:
        setup_resp = requests.post(f"{base_url}/api/vps/v1/virtual-machines/{vm_id}/setup", headers=headers, json=setup_payload)
        setup_resp.raise_for_status()
        vps_details = setup_resp.json()
    except Exception as e:
        module.fail_json(msg=f"VPS setup failed: {str(e)}")

    module.exit_json(changed=True, vps_details=vps_details)

if __name__ == '__main__':
    main()
