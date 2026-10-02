# Hostinger VPS Ansible Collection

This collection provides Ansible modules to manage Hostinger Virtual Private Servers (VPS) using Hostinger's public API.

## Included Modules

| Module Name                                              | Description                                                  |
| -------------------------------------------------------- | ------------------------------------------------------------ |
| `hostinger.vps.hostinger_vps_action_info`                | List the actions performed on a VPS, or get one              |
| `hostinger.vps.hostinger_vps_backup`                     | List or restore VPS backups                                  |
| `hostinger.vps.hostinger_vps_backup_info`                | List the backups of a VPS                                    |
| `hostinger.vps.hostinger_vps_catalog_info`               | List purchasable products and their prices                   |
| `hostinger.vps.hostinger_vps_data_center_info`           | List the data centers a VPS can be set up in                 |
| `hostinger.vps.hostinger_vps_firewall`                   | Create, delete, or get Hostinger VPS firewalls               |
| `hostinger.vps.hostinger_vps_firewall_binding`           | Activate, deactivate, or sync firewalls on a VPS             |
| `hostinger.vps.hostinger_vps_firewall_info`              | List firewalls and their rules, or get one                   |
| `hostinger.vps.hostinger_vps_firewall_rule`              | Create, update, delete firewall rules                        |
| `hostinger.vps.hostinger_vps_get_info`                   | Retrieve details about a specific Hostinger VPS              |
| `hostinger.vps.hostinger_vps_hostname`                   | Set or reset the hostname of VPS                             |
| `hostinger.vps.hostinger_vps_malware_scanner`            | Install or uninstall the malware scanner on a VPS            |
| `hostinger.vps.hostinger_vps_malware_scanner_info`       | Get the malware scanner's status and last scan results       |
| `hostinger.vps.hostinger_vps_metrics`                    | Fetch VPS metrics within a specified time range              |
| `hostinger.vps.hostinger_vps_payment_method_info`        | Retrieve a list of available payment methods                 |
| `hostinger.vps.hostinger_vps_post_install_script_info`   | List post-install scripts, or get one                        |
| `hostinger.vps.hostinger_vps_postinstall_create`         | Create post-install scripts                                  |
| `hostinger.vps.hostinger_vps_postinstall_delete`         | Delete a post-install script                                 |
| `hostinger.vps.hostinger_vps_postinstall_list`           | List available post-install scripts                          |
| `hostinger.vps.hostinger_vps_power`                      | Start, stop, or restart a VPS instance                       |
| `hostinger.vps.hostinger_vps_provision`                  | Order and set up a new VPS instance from catalog             |
| `hostinger.vps.hostinger_vps_reinstall`                  | Reinstall a VPS with a different OS/template                 |
| `hostinger.vps.hostinger_vps_snapshot`                   | Create, delete, restore, or get snapshot info                |
| `hostinger.vps.hostinger_vps_snapshot_info`              | Get the snapshot of a VPS                                    |
| `hostinger.vps.hostinger_vps_ssh_key`                    | Create, delete, or list SSH public keys                      |
| `hostinger.vps.hostinger_vps_ssh_key_binding`            | Attach SSH keys to a virtual machine                         |
| `hostinger.vps.hostinger_vps_ssh_key_info`               | List the SSH public keys of the account                      |
| `hostinger.vps.hostinger_vps_subscription_info`          | Retrieve active subscription information                     |
| `hostinger.vps.hostinger_vps_template_info`              | List OS templates, or get one                                |
| `hostinger.vps.hostinger_vps_vm_info`                    | List virtual machines, or get one                            |

## Inventory Plugin

| Plugin Name                  | Description                                 |
| --------------------------- | ------------------------------------------- |
| `hostinger.vps.inventory`   | Dynamic inventory plugin for VPS instances  |

## Requirements

- Ansible Core versions >= 2.13, with Python 3.6 or newer on the control node
- Hostinger API Token (bearer) - obtainable from your Hostinger account under the API section

Every module accepts the token through the `token` option. When it is omitted, the `HOSTINGER_API_TOKEN` environment variable is used, which is also how the inventory plugin should receive it, because inventory files are not templated.

Modules that start an action on a virtual machine (power, recreate, snapshots, backups, hostname, PTR, firewall binding, SSH key binding and the malware scanner) return as soon as the action is accepted. Set `wait: true` to wait until it has finished; `wait_timeout` sets the limit in seconds (600 by default).

Note: A valid payment method (such as Google Pay or PayPal) added to your Hostinger account is optional, and only required when provisioning new resources through the API. If you're using this collection to manage existing VPS instances, no payment method is needed.

## Usage

Install this collection and use the modules in your Ansible playbooks to control VPS lifecycle and post-install scripts.

### 📦 Install from Ansible Galaxy

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
