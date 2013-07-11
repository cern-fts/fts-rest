from M2Crypto import EVP
import re
import urllib


def voFromFqan(fqan):
	components = fqan.split('/')[1:]
	groups = []
	for c in components:
		if (c.lower().startswith('role=')):
			break
		groups.append(c)
	return '/'.join(groups)



def generateDelegationId(dn, fqans):
	d = EVP.MessageDigest('sha1')
	d.update(dn)

	if len(fqans) > 0:
		fqan = fqans[-1]
		d.update(fqan)
		
	digestFull = d.digest().encode('hex')
	# Original implementation only takes into account first 16 characters
	# See https://svnweb.cern.ch/trac/fts3/browser/trunk/src/server/ws/delegation/GSoapDelegationHandler.cpp
	return digestFull[:16]



class UserCredentials(object):
	def __init__(self, env, rolePermissions = None):
		# Default
		self.user_dn   = None
		self.dn        = []
		self.voms_cred = []
		self.vos       = []
		self.delegation_id = None
		
		# Try first GRST_ variables
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
				if vo not in self.vos:
					self.vos.append(vo)
			
			grstIndex += 1
			grstEnv = 'GRST_CRED_AURI_%d' % grstIndex
				
		# If not, try with regular SSL_
		if len(self.dn) == 0 and 'SSL_CLIENT_S_DN' in env:
			self.dn.append(urllib.unquote_plus(env['SSL_CLIENT_S_DN']))
			
			
		# Pick first one
		if len(self.dn) > 0:
			self.user_dn = self.dn[0]
			
		# Generate the delegation ID
		if self.user_dn is not None:
			self.delegation_id = generateDelegationId(self.user_dn, self.voms_cred)
			
		# Populate roles
		self.roles = self._populate_roles()
		
		# And granted level
		self.level = self._granted_level(rolePermissions)


	def _populate_roles(self):
		roles = []
		for fqan in self.voms_cred:
			match = re.match('(/.+)*/Role=(\\w+)(/.*)?', fqan, re.IGNORECASE)
			if match and match.group(2).upper() != 'NULL':
				roles.append(match.group(2))
		
		return roles

	def _granted_level(self, rolePermissions):
		if rolePermissions is None:
			return {}
			
		grantedLevel = rolePermissions['public'] if 'public' in rolePermissions else {}
		for role in self.roles:
			if role in rolePermissions:
				grantedLevel.update(rolePermissions[role])
		return grantedLevel



	def getGrantedLevelFor(self, operation):
		if operation in self.level:
			return self.level[operation]
		elif '*' in self.level:
			return self.level['*']
		else:
			return None



	def hasVo(self, vo):
		return vo in self.vos
