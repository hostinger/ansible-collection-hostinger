from ansible.module_utils.basic import AnsibleModule

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Referer": "https://hostinger.com",
    "Content-Type": "application/json",
}

def get_headers(token: str) -> dict:
    if not token:
        raise ValueError("Token is required to generate headers.")
    
    return {**BASE_HEADERS, "Authorization": f"Bearer {token}"}
