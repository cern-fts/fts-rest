from M2Crypto import EVP
import re
import urllib


def voFromFqan(fqan):
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
        if (c.lower().startswith('role=')):
            break
        groups.append(c)
    return '/'.join(groups)


def generateDelegationId(dn, fqans):
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

    if len(fqans) > 0:
        fqan = fqans[-1]
        d.update(fqan)

    digestFull = d.digest().encode('hex')
    # Original implementation only takes into account first 16 characters
    return digestFull[:16]


class UserCredentials(object):
    """
    Handles the user credentials and privileges
    """
    
    def __init__(self, env, rolePermissions=None):
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
        self.delegation_id = None

        # Try first GRST_ variables as set by mod_gridsite
        grstIndex = 0
        grstEnv = 'GRST_CRED_AURI_%d' % grstIndex
        while grstEnv in env:
            cred = env[grstEnv]

            if cred.startswith('dn:'):
                self.dn.append(urllib.unquote_plus(cred[3:]))
            elif cred.startswith('fqan:'):
                fqan = urllib.unquote_plus(cred[5:])
                vo   = voFromFqan(fqan)
                self.voms_cred.append(fqan)
                if vo not in self.vos and vo:
                    self.vos.append(vo)

            grstIndex += 1
            grstEnv = 'GRST_CRED_AURI_%d' % grstIndex

        # If not, try with regular SSL_ as set by mod_ssl
        if len(self.dn) == 0 and 'SSL_CLIENT_S_DN' in env:
            self.dn.append(urllib.unquote_plus(env['SSL_CLIENT_S_DN']))

        # Pick first one
        if len(self.dn) > 0:
            self.user_dn = self.dn[0]

        # Generate the delegation ID
        if self.user_dn is not None:
            self.delegation_id = generateDelegationId(self.user_dn,
                                                      self.voms_cred)

        # If no vo information is available, assume nil
        if not self.vos:
            self.vos.append('nil')

        # Populate roles
        self.roles = self._populate_roles()

        # And granted level
        self.level = self._granted_level(rolePermissions)

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

    def _granted_level(self, rolePermissions):
        """
        Get all granted levels for this user out of the configuration
        (all levels authorized for public, plus those for the given Roles)
        """
        if rolePermissions is None:
            return {}

        if 'public' in rolePermissions:
            grantedLevel = rolePermissions['public']
        else:
            grantedLevel = {}

        for role in self.roles:
            if role in rolePermissions:
                grantedLevel.update(rolePermissions[role])
        return grantedLevel

    def getGrantedLevelFor(self, operation):
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

    def hasVo(self, vo):
        """
        Check if the user belongs to the given VO
        
        Args:
            vo: The VO name (i.e. dteam)

        Returns:
            True if the user credentials include the given VO
        """
        return vo in self.vos
