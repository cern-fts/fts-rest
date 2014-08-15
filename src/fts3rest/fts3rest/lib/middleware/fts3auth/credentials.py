#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re
from M2Crypto import EVP

from methods import do_authentication


def vo_from_fqan(fqan):
    """
    Get the VO from a full FQAN

    Args:
        fqan: A single fqans (i.e. /dteam/cern/Role=lcgadmin)
    Returns:
        The vo + group (i.e. dteam/cern)
    """
    components = fqan.split('/')[1:]
    groups = []
    for c in components:
        if c.lower().startswith('role='):
            break
        groups.append(c)
    return '/'.join(groups)


def generate_delegation_id(dn, fqans):
    """
    Generate a delegation ID from the user DN and FQANS
    Adapted from FTS3
    See https://svnweb.cern.ch/trac/fts3/browser/trunk/src/server/ws/delegation/GSoapDelegationHandler.cpp

    Args:
        dn:    The user DN
        fqans: A list of fqans
    Returns:
        The associated delegation id
    """
    d = EVP.MessageDigest('sha1')
    d.update(dn)

    for fqan in fqans:
        d.update(fqan)

    digest_hex = d.digest().encode('hex')
    # Original implementation only takes into account first 16 characters
    return digest_hex[:16]


def build_vo_from_dn(user_dn):
    """
    Generate an 'anonymous' VO from the user_dn
    """
    components = filter(lambda c: len(c) == 2, map(lambda c: tuple(c.split('=')), user_dn.split('/')))
    domain = []
    uname = ''
    for key, value in components:
        if key.upper() == 'CN':
            uname = value
        elif key.upper() == 'DC':
            domain.append(value)
    # Normalize name
    uname = ''.join(uname.split())
    return uname + '@' + '.'.join(reversed(domain))


class UserCredentials(object):
    """
    Handles the user credentials and privileges
    """

    def _anonymous(self):
        """
        Not authenticated access
        """
        self.user_dn = 'anon'
        self.method = 'unauthenticated'

    def __init__(self, env, role_permissions=None):
        """
        Constructor

        Args:
            env:             Environment (i.e. os.environ)
            rolePermissions: The role permissions as configured in the FTS3 config file
        """
        # Default
        self.user_dn   = None
        self.dn        = []
        self.voms_cred = []
        self.vos       = []
        self.roles     = []
        self.level     = []
        self.delegation_id = None
        self.method    = None

        # Try certificate-based authentication
        got_creds = do_authentication(self, env)

        # Last resort: anonymous access
        if not got_creds:
            self._anonymous()
        else:
            # Populate roles
            self.roles = self._populate_roles()
            # And granted level
            self.level = self._granted_level(role_permissions)

    def _populate_roles(self):
        """
        Get roles out of the FQANS
        """
        roles = []
        for fqan in self.voms_cred:
            match = re.match('(/.+)*/Role=(\\w+)(/.*)?', fqan, re.IGNORECASE)
            if match and match.group(2).upper() != 'NULL':
                roles.append(match.group(2))
        return roles

    def _granted_level(self, role_permissions):
        """
        Get all granted levels for this user out of the configuration
        (all levels authorized for public, plus those for the given Roles)
        """
        if role_permissions is None:
            return {}

        if 'public' in role_permissions:
            granted_level = role_permissions['public']
        else:
            granted_level = {}

        for role in self.roles:
            if role in role_permissions:
                granted_level.update(role_permissions[role])
        return granted_level

    def get_granted_level_for(self, operation):
        """
        Check if the user can perform the operation 'operation'

        Args:
            operation: The operation to check (see constants.py)

        Returns:
            None if the user can not perform the operation
            constants.VO if only can perform it on same VO resources
            constants.ALL if can perform on any resource
            constants.PRIVATE if can perform only on his/her own resources
        """
        if operation in self.level:
            return self.level[operation]
        elif '*' in self.level:
            return self.level['*']
        else:
            return None

    def has_vo(self, vo):
        """
        Check if the user belongs to the given VO

        Args:
            vo: The VO name (i.e. dteam)

        Returns:
            True if the user credentials include the given VO
        """
        return vo in self.vos
