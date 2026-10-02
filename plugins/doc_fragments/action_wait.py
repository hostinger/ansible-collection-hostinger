# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
  wait:
    description:
      - Wait until the action started on the virtual machine has finished.
      - When enabled, the returned action shows its final state, and the module fails if the action fails or does
        not finish within I(wait_timeout).
    type: bool
    default: false
    version_added: 1.1.0
  wait_timeout:
    description:
      - Maximum number of seconds to wait when I(wait=true).
    type: int
    default: 600
    version_added: 1.1.0
'''
