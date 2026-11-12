##############################
Hostinger Collection Release Notes
##############################

.. contents:: Topics

v1.1.0
======

Breaking Changes
----------------
- `hostinger_vps_ssh_key_binding` now calls `POST /virtual-machines/{id}/ssh-keys` because the old `public-keys/attach` endpoint is deprecated. It takes key text in the new `keys` option, which replaces `public_key_ids`, and no longer takes `wait` (the API returns the key list, not an action).
- Resource ID options (`virtual_machine_id`, `firewall_id`, `rule_id`, `backup_id`, `public_key_id`, `post_install_script_id`) are now integers, so a value can no longer change the API path a module calls.

Security Fixes
--------------
- The inventory plugin marks the host names and variables it reads from the API as unsafe, so ansible-core older than 2.19 no longer evaluates Jinja2 in them.
- The inventory plugin no longer lets a VM take the name `localhost` or another VM's hostname; such VMs are added as `srv<id>.hstgr.cloud` with a warning.

v1.0.0
======

Modules
-----------
- `hostinger_vps_firewall`
- `hostinger_vps_firewall_binding`
- `hostinger_vps_firewall_rule`
- `hostinger_vps_get_info`
- `hostinger_vps_malware_scanner`
- `hostinger_vps_metrics`
- `hostinger_vps_payment_method_info`
- `hostinger_vps_postinstall_create`
- `hostinger_vps_postinstall_delete`
- `hostinger_vps_postinstall_list`
- `hostinger_vps_power`
- `hostinger_vps_provision`
- `hostinger_vps_reinstall`
- `hostinger_vps_snapshot`
- `hostinger_vps_ssh_key`
- `hostinger_vps_ssh_key_binding`
- `hostinger_vps_subscription_info`
