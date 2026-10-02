#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: hostinger_vps_firewall_rule
short_description: Manage Hostinger VPS firewall rules
description:
  - Add, update, or delete firewall rules for Hostinger VPS.
options:
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
      - The protocol is matched case-insensitively against C(TCP), C(UDP), C(ICMP), C(ICMPv6), C(GRE), C(ESP), C(AH),
        C(SSH), C(HTTP), C(HTTPS), C(MySQL), C(PostgreSQL) and C(any).
    required: false
    type: dict
  state:
    description:
      - Desired rule operation.
    required: true
    type: str
    choices: [create, update, delete]
extends_documentation_fragment:
  - hostinger.vps.api
author:
  - Hostinger Dev Team (@hostinger)
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

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    HostingerApiError,
    api_argument_spec,
    client_from_module,
    fail_on_api_error,
)

PROTOCOLS = [
    'TCP', 'UDP', 'ICMP', 'ICMPv6', 'GRE', 'ESP', 'AH',
    'SSH', 'HTTP', 'HTTPS', 'MySQL', 'PostgreSQL', 'any'
]


def normalize_protocol(protocol):
    """Return the protocol in the exact casing the API accepts, or None when it is not a valid protocol."""
    for valid_protocol in PROTOCOLS:
        if valid_protocol.lower() == str(protocol).lower():
            return valid_protocol
    return None


def is_valid_cidr(value):
    # Very basic CIDR/IP format checker
    return re.match(r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$', value) is not None


def main():
    module_args = api_argument_spec()
    module_args.update(
        firewall_id=dict(type='str', required=True),
        rule_id=dict(type='str', required=False),
        rule=dict(type='dict', required=False),
        state=dict(type='str', required=True, choices=["create", "update", "delete"])
    )

    module = AnsibleModule(argument_spec=module_args)
    firewall_id = module.params["firewall_id"]
    rule_id = module.params.get("rule_id")
    rule = module.params.get("rule")
    state = module.params["state"]

    if state in ["create", "update"]:
        if not rule:
            module.fail_json(msg="The 'rule' parameter is required for create/update.")

        # Validate and normalize protocol
        if "protocol" not in rule:
            module.fail_json(msg="'protocol' must be specified in the rule.")
        protocol = normalize_protocol(rule["protocol"])
        if protocol is None:
            module.fail_json(msg=f"Invalid protocol '{rule['protocol']}'. Must be one of: {', '.join(PROTOCOLS)}")
        rule["protocol"] = protocol

        # Validate source and source_detail
        if "source" not in rule:
            module.fail_json(msg="'source' must be specified in the rule.")
        if "source_detail" not in rule or not rule["source_detail"]:
            module.fail_json(msg="'source_detail' must be provided for all rules ex.: source_detail: any.")

        if rule["source"] == "custom" and not is_valid_cidr(rule["source_detail"]):
            module.fail_json(msg="When 'source' is 'custom', 'source_detail' must be a valid IP or CIDR (e.g., '192.168.1.0/24').")

    if state in ["update", "delete"] and not rule_id:
        module.fail_json(msg=f"'rule_id' is required for {state}.")

    try:
        client = client_from_module(module)
        if state == "create":
            result = client.post(f"/api/vps/v1/firewall/{firewall_id}/rules", body=rule)
        elif state == "update":
            result = client.put(f"/api/vps/v1/firewall/{firewall_id}/rules/{rule_id}", body=rule)
        else:
            result = client.delete(f"/api/vps/v1/firewall/{firewall_id}/rules/{rule_id}")
    except HostingerApiError as error:
        fail_on_api_error(module, error, f"Firewall rule {state}")

    module.exit_json(changed=True, rule=result)


if __name__ == "__main__":
    main()
