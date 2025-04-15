# Hostinger VPS Ansible Collection

This collection provides Ansible modules to manage Hostinger Virtual Private Servers (VPS) using Hostinger's public API.

## Included Modules

| Module Name                                      | Description                                                  |
| ------------------------------------------------ | ------------------------------------------------------------ |
| `hostinger.vps.hostinger_vps_firewall`           | Manage Hostinger VPS firewalls (create, delete, get, update) |
| `hostinger.vps.hostinger_vps_firewall_binding`   | Attach, detach, or sync firewalls to/from a VPS              |
| `hostinger.vps.hostinger_vps_firewall_rule`      | Create, update, delete firewall rules                        |
| `hostinger.vps.hostinger_vps_get_info`           | Retrieve details about a specific Hostinger VPS              |
| `hostinger.vps.hostinger_vps_hostname`           | Set or reset the hostname of VPS                             |
| `hostinger.vps.hostinger_vps_malware_scanner`    | Install or uninstall the malware scanner on a VPS            |
| `hostinger.vps.hostinger_vps_metrics`            | Fetch VPS metrics within a specified time range              |
| `hostinger.vps.hostinger_vps_payment_method_info`| Retrieve a list of available payment methods                 |
| `hostinger.vps.hostinger_vps_postinstall_create` | Create post-install scripts                                  |
| `hostinger.vps.hostinger_vps_postinstall_delete` | Delete a post-install script                                 |
| `hostinger.vps.hostinger_vps_postinstall_list`   | List available post-install scripts                          |
| `hostinger.vps.hostinger_vps_power`              | Start, stop, or restart a VPS instance                       |
| `hostinger.vps.hostinger_vps_provision`          | Order and set up a new VPS instance from catalog             |
| `hostinger.vps.hostinger_vps_reinstall`          | Reinstall a VPS with a different OS/template                 |
| `hostinger.vps.hostinger_vps_snapshot`           | Create, delete, restore, or get snapshot info                |
| `hostinger.vps.hostinger_vps_ssh_key`            | Create, delete, or list SSH public keys                      |
| `hostinger.vps.hostinger_vps_ssh_key_binding`    | Attach SSH keys to a virtual machine                         |
| `hostinger.vps.hostinger_vps_subscription_info`  | Retrieve active subscription information                     |

## Inventory Plugin

| Plugin Name                  | Description                                 |
| --------------------------- | ------------------------------------------- |
| `hostinger.vps.hostinger`   | Dynamic inventory plugin for VPS instances  |


## Usage

Install this collection and use the modules in your Ansible playbooks to control VPS lifecycle and post-install scripts.

### 📦 Install from Ansible Galaxy (once published)

```bash
ansible-galaxy collection install hostinger.vps
```

### 🛠️ Install Locally for Development

```bash
ansible-galaxy collection build
ansible-galaxy collection install hostinger-vps-*.tar.gz
```

---

## Contributing

Pull requests and issues are welcome.

If you encounter any bugs or unexpected behavior, please [open an issue](https://github.com/hostinger/ansible-collection-hostinger/issues).  
Our team actively monitors reports and strives to address them promptly to ensure a stable and reliable experience for all users.
