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

from collections import Counter

from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.utils.unsafe_proxy import wrap_var
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

        vms = [vm for vm in vms if isinstance(vm, dict)]
        hostname_counts = Counter(vm.get("hostname") for vm in vms)

        for vm in vms:
            # The API hostname is chosen by whoever manages the VM, so it must not claim localhost
            # or another VM's name; such VMs fall back to their unique default hostname.
            fallback = f"srv{vm.get('id', 'unknown')}.hstgr.cloud"
            hostname = vm.get("hostname")
            if not hostname or hostname in C.LOCALHOST or hostname_counts[hostname] > 1:
                if hostname:
                    self.display.warning(
                        f"Hostinger VM {vm.get('id')} has hostname '{hostname}', which is local or shared by another VM; adding it as {fallback}."
                    )
                hostname = fallback
            hostname = wrap_var(hostname)

            if hostname in self.inventory.hosts:
                self.display.warning(f"Skipping Hostinger VM {vm.get('id')}: the inventory already has a host named {hostname}.")
                continue

            self.inventory.add_host(hostname)

            ipv4_list = vm.get("ipv4") or []
            ip = ipv4_list[0]["address"] if ipv4_list and "address" in ipv4_list[0] else None
            if ip:
                self._set_variable(hostname, "ansible_host", ip)

            for name in ("plan", "state", "cpus", "memory", "disk"):
                self._set_variable(hostname, name, vm.get(name))
            self._set_variable(hostname, "hostinger_id", vm.get("id"))

    def _set_variable(self, hostname, name, value):
        # API values are data, never templates: mark them unsafe so Ansible does not evaluate Jinja2 in them.
        self.inventory.set_variable(hostname, name, wrap_var(value))
