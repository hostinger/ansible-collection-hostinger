##############################
Hostinger Collection Release Notes
##############################

.. contents:: Topics

v1.1.0
======

Breaking Changes
----------------
- `hostinger_vps_ssh_key_binding` now calls `POST /virtual-machines/{id}/ssh-keys` because the old `public-keys/attach` endpoint is deprecated. It takes key text in the new `keys` option, which replaces `public_key_ids`, and no longer takes `wait` (the API returns the key list, not an action).

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
