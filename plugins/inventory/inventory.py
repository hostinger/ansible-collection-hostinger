# plugins/inventory/inventory.py
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: inventory
short_description: Hostinger VPS inventory plugin
description:
  - Collects Hostinger VPS instances as dynamic Ansible inventory using the Hostinger VPS API.
options:
  plugin:
    description: Token to indicate this is a Hostinger inventory plugin
    required: true
    type: string
    choices: [hostinger.vps.inventory]
  token:
    description:
      - Bearer token to access the Hostinger API.
      - Inventory files are not templated, so set the token directly or through the C(HOSTINGER_API_TOKEN) environment variable.
    required: true
    type: string
    env:
      - name: HOSTINGER_API_TOKEN
  api_url:
    description: Base URL of the Hostinger API.
    type: string
    default: https://developers.hostinger.com
    version_added: 1.1.0
  api_timeout:
    description: Timeout in seconds for each API request.
    type: integer
    default: 60
    version_added: 1.1.0
'''

EXAMPLES = r'''
# hostinger.yml, used with HOSTINGER_API_TOKEN set in the environment
plugin: hostinger.vps.inventory
'''

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible_collections.hostinger.vps.plugins.module_utils.api import (
    DEFAULT_API_URL,
    DEFAULT_TIMEOUT,
    HostingerApiClient,
    HostingerApiError,
)


class InventoryModule(BaseInventoryPlugin):
    NAME = 'hostinger.vps.inventory'

    def verify_file(self, path):
        return super().verify_file(path) and path.endswith(('.yml', '.yaml'))

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)
        self._read_config_data(path)

        client = HostingerApiClient(
            token=self.get_option('token'),
            api_url=self.get_option('api_url') or DEFAULT_API_URL,
            timeout=self.get_option('api_timeout') or DEFAULT_TIMEOUT,
        )

        try:
            vms = client.get("/api/vps/v1/virtual-machines")
        except HostingerApiError as error:
            raise AnsibleError(f"Failed to fetch virtual machines from the Hostinger API: {error}")

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
