from M2Crypto import EVP
import urllib


def voFromFqan(fqan):
	components = fqan.split('/')[1:]
	components = filter(lambda x: not x.endswith('=NULL'), components)
	return '/'.join(components)



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
	def __init__(self, env):
		# Default
		self.user_dn   = None
		self.voms_cred = []
		self.vos       = []
		
		# Try first GRST_ variables
		grstIndex = 0
		grstEnv = 'GRST_CRED_AURI_%d' % grstIndex
		while grstEnv in env:
			cred = env[grstEnv]
			
			if cred.startswith('dn:') and self.user_dn is None:
				self.user_dn = urllib.unquote_plus(cred[3:])
			elif cred.startswith('fqan:'):
				fqan = urllib.unquote_plus(cred[5:])
				vo   = voFromFqan(fqan)
				self.voms_cred.append(fqan)
				self.vos.append(vo)
				
			
			grstIndex += 1
			grstEnv = 'GRST_CRED_AURI_%d' % grstIndex
		
		# If not, try with regular SSL_
		if self.user_dn is None and 'SSL_CLIENT_S_DN' in env:
			self.user_dn = urllib.unquote_plus(env['SSL_CLIENT_S_DN'])
			
		# Generate the delegation ID
		self.delegation_id = generateDelegationId(self.user_dn, self.voms_cred)
		