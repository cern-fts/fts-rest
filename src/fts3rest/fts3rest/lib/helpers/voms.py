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

from datetime import datetime, timedelta
from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
import logging
import os

log = logging.getLogger(__name__)


class VomsException(Exception):
    """
    Exception thrown by the VOMS client wrapper
    """
    def __int__(self, *args, **kwargs):
        super(self, VomsException).__init__(args, kwargs)


def _check_proxy_validity(proxy_path):
    """
    voms-proxy-init may return != 0 even when the proxy was created
    (something to do with the remaining lifetime), so check the validity
    using voms-proxy-info
    """
    args = ['voms-proxy-info', '--file', proxy_path, '--exists']
    log.debug(' '.join(args))
    proc = Popen(args, shell=False, stdin=None, stdout=None, stderr=None)
    return proc.wait() == 0


def _get_proxy_termination_time(proxy_path):
    """
    Get the termination time of the proxy specified by proxy_path
    """
    args = ['voms-proxy-info', '--file', proxy_path, '--timeleft', '--actimeleft']
    log.debug(' '.join(args))

    proc = Popen(args, shell=False, stdin=None, stdout=PIPE, stderr=STDOUT)
    out = ''
    for l in proc.stdout:
        out += l
    rcode = proc.wait()
    if rcode != 0:
        raise VomsException('Failed to get the termination time of a proxy: ' + out)

    try:
        timeleft = min([int(v) for v in out.split('\n') if v])
        return datetime.utcnow() + timedelta(seconds=timeleft)
    except Exception, e:
        raise VomsException('Failed to get the termination time of a proxy: ' + str(e))


class VomsClient(object):
    """
    Wrapper for the VOMS client
    """

    def __init__(self, proxy):
        proxy_fd = NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
        proxy_fd.write(proxy)
        proxy_fd.close()
        self.proxy_path = proxy_fd.name

    def __del__(self):
        os.unlink(self.proxy_path)

    def init(self, voms_list, lifetime=None):
        """
        Generates a new proxy with additional voms attributes

        Args:
            voms_list: A list of voms attributes (['dteam', 'dteam:/dteam/Role=lcgadmin])
            lifetime:  The new proxy lifetime in minutes

        Returns:
            A tuple (proxy PEM encoded, new termination time)

        Raises:
            VomsException: There was an 'expected' error getting the proxy
                           Meaning: The user requested a voms to which he/she doesn't belong
        """
        new_proxy = self._voms_proxy_init(voms_list, lifetime)
        new_termination_time = _get_proxy_termination_time(new_proxy)

        new_proxy_pem = open(new_proxy).read()
        os.unlink(new_proxy)

        return new_proxy_pem, new_termination_time

    def _voms_proxy_init(self, voms_list, lifetime):
        """
        Call voms-proxy-init to get the new voms extensions
        """
        new_proxy = NamedTemporaryFile(mode='w', suffix='.pem', delete=False).name

        args = ['voms-proxy-init',
                '--cert', self.proxy_path,
                '--key', self.proxy_path,
                '--out', new_proxy,
                '--noregen', '--ignorewarn']
        for v in voms_list:
            args.extend(('--voms', v))
        if lifetime:
            args.extend(('--valid', "%d:%d" % (lifetime / 60, lifetime % 60)))

        log.debug(' '.join(args))

        proc = Popen(args, shell=False, stdin=None, stdout=PIPE, stderr=STDOUT)
        out = ''
        for l in proc.stdout:
            out += l
        rcode = proc.wait()
        if rcode != 0 and not _check_proxy_validity(new_proxy):
            raise VomsException("Failed to generate a proxy (%d): %s" % (rcode, out))

        return new_proxy
