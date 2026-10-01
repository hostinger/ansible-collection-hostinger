# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.module_utils.urls import ConnectionError as UrlsConnectionError, open_url

DEFAULT_API_URL = "https://developers.hostinger.com"
DEFAULT_TIMEOUT = 60
TOKEN_ENV_VAR = "HOSTINGER_API_TOKEN"

# Cloudflare in front of the API rejects requests that do not identify themselves (issue #1).
USER_AGENT = "ansible-collection-hostinger"


def api_argument_spec():
    """Options shared by every module; documented in the hostinger.vps.api doc fragment."""
    return dict(
        token=dict(type="str", required=True, no_log=True, fallback=(env_fallback, [TOKEN_ENV_VAR])),
        api_url=dict(type="str", default=DEFAULT_API_URL),
        api_timeout=dict(type="int", default=DEFAULT_TIMEOUT),
    )


class HostingerApiError(Exception):
    """Raised for any failed API call; status_code and response are None for network errors."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class HostingerApiClient:
    def __init__(self, token, api_url=DEFAULT_API_URL, timeout=DEFAULT_TIMEOUT):
        if not token:
            raise HostingerApiError(f"An API token is required. Set the token option or the {TOKEN_ENV_VAR} environment variable.")

        self.api_url = (api_url or DEFAULT_API_URL).rstrip("/")
        self.timeout = timeout
        self.last_status_code = None
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def request(self, method, path, body=None, query=None):
        """Send a request and return the decoded JSON body, or {} when the body is empty."""
        url = self.api_url + path
        if query:
            url = f"{url}?{urlencode(query)}"

        data = to_bytes(json.dumps(body)) if body is not None else None

        try:
            response = open_url(
                url,
                method=method,
                data=data,
                headers=self.headers,
                http_agent=USER_AGENT,
                timeout=self.timeout,
            )
            self.last_status_code = response.getcode()
            content = response.read()
        except HTTPError as error:
            raise self._http_error(method, path, error)
        except (URLError, UrlsConnectionError, OSError) as error:
            reason = getattr(error, "reason", error)
            raise HostingerApiError(f"{method} {path} failed: {to_native(reason)}")

        return self._decode(method, path, content)

    def get(self, path, query=None):
        return self.request("GET", path, query=query)

    def post(self, path, body=None):
        return self.request("POST", path, body=body)

    def put(self, path, body=None):
        return self.request("PUT", path, body=body)

    def delete(self, path):
        return self.request("DELETE", path)

    def get_all_pages(self, path, query=None):
        """Follow the page parameter of a paginated endpoint and return the items of every page."""
        items = []
        page = 1

        while True:
            result = self.get(path, query=dict(query or {}, page=page))
            data = result.get("data") or []
            items.extend(data)

            meta = result.get("meta") or {}
            per_page = meta.get("per_page") or len(data)
            if not data or page * per_page >= meta.get("total", 0):
                return items

            page += 1

    @staticmethod
    def _decode(method, path, content):
        if not content:
            return {}

        try:
            return json.loads(to_text(content))
        except ValueError:
            raise HostingerApiError(f"{method} {path} returned a response that is not valid JSON: {to_native(content)[:200]}")

    @staticmethod
    def _http_error(method, path, error):
        try:
            raw = error.read()
        except Exception:
            raw = b""

        try:
            response = json.loads(to_text(raw)) if raw else None
        except ValueError:
            response = to_text(raw)

        details = to_native(error.reason)
        if isinstance(response, dict):
            field_errors = response.get("errors")
            if isinstance(field_errors, dict) and field_errors:
                # The message only repeats the first field error, so list them all instead.
                details = "; ".join(
                    f"{field}: {' '.join(messages) if isinstance(messages, list) else messages}"
                    for field, messages in field_errors.items()
                )
            else:
                details = response.get("message") or details
        elif response:
            details = response[:200]

        return HostingerApiError(
            f"{method} {path} returned HTTP {error.code}: {details}",
            status_code=error.code,
            response=response,
        )


def client_from_module(module):
    return HostingerApiClient(
        token=module.params["token"],
        api_url=module.params["api_url"],
        timeout=module.params["api_timeout"],
    )


def fail_on_api_error(module, error, action):
    """Fail the module with the API error, keeping the HTTP status and parsed body in the result."""
    module.fail_json(
        msg=f"{action} failed: {error}",
        status_code=error.status_code,
        response=error.response,
    )
