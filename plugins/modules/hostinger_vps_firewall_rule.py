#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.headers import get_headers
import requests
import re

DOCUMENTATION = '''
---
module: hostinger_vps_firewall_rule
short_description: Manage Hostinger VPS firewall rules
description:
  - Add, update, or delete firewall rules for Hostinger VPS.
options:
  token:
    description: Hostinger API token
    required: true
    type: str
  firewall_id:
    description: ID of the firewall to manage rules for
    required: true
    type: str
  rule_id:
    description: Rule ID (required for update/delete)
    required: false
    type: str
  rule:
    description:
      - Dictionary with rule parameters.
      - Required for create and update.
      - Must include port, protocol, source, and source_detail.
    required: false
    type: dict
  state:
    description:
      - Desired rule operation.
    required: true
    type: str
    choices: [create, update, delete]
author:
  - Hostinger Dev Team
'''

EXAMPLES = '''
- name: Create a rule allowing SSH from anywhere
  hostinger.vps.hostinger_vps_firewall_rule:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    state: create
    rule:
      port: "22"
      protocol: "tcp"
      source: "custom"
      source_detail: "0.0.0.0/0"

- name: Update a rule to allow only from internal network
  hostinger.vps.hostinger_vps_firewall_rule:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    rule_id: "246950"
    state: update
    rule:
      port: "22"
      protocol: "tcp"
      source: "custom"
      source_detail: "10.0.0.0/8"

- name: Delete a rule
  hostinger.vps.hostinger_vps_firewall_rule:
    token: "{{ hostinger_token }}"
    firewall_id: "72122"
    rule_id: "246950"
    state: delete
'''

RETURN = '''
rule:
  description: Firewall rule result
  returned: always
  type: dict
'''

def is_valid_cidr(value):
    # Very basic CIDR/IP format checker
    return re.match(r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$', value) is not None

def main():
    module_args = dict(
        token=dict(type='str', required=True, no_log=True),
        firewall_id=dict(type='str', required=True),
        rule_id=dict(type='str', required=False),
        rule=dict(type='dict', required=False),
        state=dict(type='str', required=True, choices=["create", "update", "delete"])
    )

    module = AnsibleModule(argument_spec=module_args)
    token = module.params["token"]
    firewall_id = module.params["firewall_id"]
    rule_id = module.params.get("rule_id")
    rule = module.params.get("rule")
    state = module.params["state"]

    headers = get_headers(token)

    valid_protocols = [
        'TCP', 'UDP', 'ICMP', 'ICMPv6', 'GRE', 'ESP', 'AH',
        'SSH', 'HTTP', 'HTTPS', 'MySQL', 'PostgreSQL', 'any'
    ]

    if state in ["create", "update"]:
        if not rule:
            module.fail_json(msg="The 'rule' parameter is required for create/update.")

        # Validate and normalize protocol
        if "protocol" not in rule:
            module.fail_json(msg="'protocol' must be specified in the rule.")
        rule["protocol"] = rule["protocol"].upper()
        if rule["protocol"] not in valid_protocols:
            module.fail_json(msg=f"Invalid protocol '{rule['protocol']}'. Must be one of: {', '.join(valid_protocols)}")

        # Validate source and source_detail
        if "source" not in rule:
            module.fail_json(msg="'source' must be specified in the rule.")
        if "source_detail" not in rule or not rule["source_detail"]:
            module.fail_json(msg="'source_detail' must be provided for all rules ex.: source_detail: any.")

        if rule["source"] == "custom" and not is_valid_cidr(rule["source_detail"]):
            module.fail_json(msg="When 'source' is 'custom', 'source_detail' must be a valid IP or CIDR (e.g., '192.168.1.0/24').")

    try:
        if state == "create":
            url = f"https://developers.hostinger.com/api/vps/v1/firewall/{firewall_id}/rules"
            resp = requests.post(url, headers=headers, json=rule)

        elif state == "update":
            if not rule_id:
                module.fail_json(msg="'rule_id' is required for update.")
            url = f"https://developers.hostinger.com/api/vps/v1/firewall/{firewall_id}/rules/{rule_id}"
            resp = requests.put(url, headers=headers, json=rule)

        elif state == "delete":
            if not rule_id:
                module.fail_json(msg="'rule_id' is required for delete.")
            url = f"https://developers.hostinger.com/api/vps/v1/firewall/{firewall_id}/rules/{rule_id}"
            resp = requests.delete(url, headers=headers)

        else:
            module.fail_json(msg="Invalid state.")

        if resp.status_code in [200, 201, 202, 204]:
            result = resp.json() if resp.content else {}
            module.exit_json(changed=(state != "get"), rule=result)
        else:
            module.fail_json(msg=f"Firewall rule {state} failed. Status: {resp.status_code}. Response: {resp.text}")

    except requests.RequestException as e:
        module.fail_json(msg=f"Request failed: {e}")

if __name__ == "__main__":
    main()
