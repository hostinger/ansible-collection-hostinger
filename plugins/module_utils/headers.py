from ansible.module_utils.basic import AnsibleModule

BASE_HEADERS = {
    "User-Agent": "ansible-collection-hostinger",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def get_headers(token: str) -> dict:
    if not token:
        raise ValueError("Token is required to generate headers.")
    
    return {**BASE_HEADERS, "Authorization": f"Bearer {token}"}
