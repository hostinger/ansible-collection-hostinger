# plugins/inventory/inventory.py

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import requests
from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.module_utils._text import to_text

DOCUMENTATION = r'''
name: hostinger.vps.inventory
plugin_type: inventory
short_description: Hostinger VPS inventory plugin
description:
  - Collects Hostinger VPS instances as dynamic Ansible inventory using the Hostinger VPS API.
options:
  plugin:
    description: Token to indicate this is a Hostinger inventory plugin
    required: true
    type: string
  token:
    description: Bearer token to access the Hostinger API
    required: true
    type: string
'''

class InventoryModule(BaseInventoryPlugin):
    NAME = 'hostinger.vps.inventory'

    def verify_file(self, path):
        return super().verify_file(path) and path.endswith(('.yml', '.yaml'))

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)
        config = self._read_config_data(path)

        token = config.get('token')
        if not token:
            raise AnsibleError("Missing required 'token' in Hostinger inventory config file.")

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            resp = requests.get("https://developers.hostinger.com/api/vps/v1/virtual-machines", headers=headers)
            resp.raise_for_status()
            vms = resp.json()

            if not isinstance(vms, list):
                raise AnsibleError("Unexpected response format from Hostinger API. Expected a list of VMs.")

            for vm in vms:
                if not isinstance(vm, dict):
                    continue

                hostname = vm.get("hostname") or f"srv{vm.get('id', 'unknown')}.hstgr.cloud"
                self.inventory.add_host(hostname)

                ipv4_list = vm.get("ipv4") or []
                ip = ipv4_list[0]["address"] if ipv4_list and "address" in ipv4_list[0] else None
                if ip:
                    self.inventory.set_variable(hostname, "ansible_host", ip)

                self.inventory.set_variable(hostname, "hostinger_id", vm.get("id"))
                self.inventory.set_variable(hostname, "plan", vm.get("plan"))
                self.inventory.set_variable(hostname, "state", vm.get("state"))
                self.inventory.set_variable(hostname, "cpus", vm.get("cpus"))
                self.inventory.set_variable(hostname, "memory", vm.get("memory"))
                self.inventory.set_variable(hostname, "disk", vm.get("disk"))

        except requests.exceptions.RequestException as e:
            raise AnsibleError(f"Failed to connect to Hostinger API: {to_text(e)}")
        except ValueError:
            raise AnsibleError("Invalid JSON response from Hostinger API")

