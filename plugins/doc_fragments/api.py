# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
  token:
    description:
      - Hostinger API token.
      - If not set, the value of the C(HOSTINGER_API_TOKEN) environment variable is used.
    required: true
    type: str
  api_url:
    description:
      - Base URL of the Hostinger API.
    type: str
    default: https://developers.hostinger.com
    version_added: 1.1.0
  api_timeout:
    description:
      - Timeout in seconds for each API request.
    type: int
    default: 60
    version_added: 1.1.0
'''
