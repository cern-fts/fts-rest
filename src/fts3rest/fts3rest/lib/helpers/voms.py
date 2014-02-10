from datetime import datetime, timedelta
from subprocess import call, Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
import logging
import os

log = logging.getLogger(__name__)

class VomsException(Exception):

    def __int__(self, *args, **kwargs):
        super(self, VomsException).__init__(args, kwargs)


class VomsClient(object):
    
    def __init__(self, proxy):
        proxy_fd = NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
        proxy_fd.write(proxy)
        proxy_fd.close()
        self.proxy_path = proxy_fd.name
        
    def __del__(self):
        os.unlink(self.proxy_path)

    def init(self, voms_list, lifetime = None):
        new_proxy = self._voms_proxy_init(voms_list, lifetime)
        new_termination_time = self._get_termination_time(new_proxy)
        
        new_proxy_pem = open(new_proxy).read()
        
        return (new_proxy_pem, new_termination_time)

    def _check_validity(self, proxy_path):
        # voms-proxy-init may return != 0 even when the proxy was created
        # (something to do with the remaining lifetime)
        args = ['voms-proxy-info', '--file', proxy_path, '--exists']
        log.debug(' '.join(args))
        proc = Popen(args, shell = False, stdin = None, stdout = None, stderr = None)
        return proc.wait() == 0

    def _valid_from_timestamp(self, lifetime):
        return "%d:%d" % (lifetime / 60, lifetime % 60)

    def _voms_proxy_init(self, voms_list, lifetime):
        new_proxy = NamedTemporaryFile(mode='w', suffix='.pem', delete=False).name

        args = ['voms-proxy-init',
                '--cert', self.proxy_path,
                '--key', self.proxy_path,
                '--out', new_proxy,
                '--noregen', '--ignorewarn', '--quiet']
        for v in voms_list:
            args.extend(('--voms', v))
        if lifetime:
            args.extend(('--valid', _valid_from_timestamp(lifetime)))
            
        log.debug(' '.join(args))
            
        proc = Popen(args, shell = False, stdin = None, stdout = PIPE, stderr = STDOUT)
        out = ''
        for l in proc.stdout:
            out += l
        rcode = proc.wait()
        if rcode != 0 and not self._check_validity(new_proxy):
            raise VomsException("Failed to generate a proxy (%d): %s" % (rcode, out))
        
        return new_proxy

    def _get_termination_time(self, proxy_path):
        args = ['voms-proxy-info', '--file', proxy_path, '--timeleft', '--actimeleft']
        log.debug(' '.join(args))
        
        proc = Popen(args, shell = False, stdin = None, stdout = PIPE, stderr = STDOUT)
        out = ''
        for l in proc.stdout:
            out += l
        rcode = proc.wait()
        if rcode != 0:
            raise VomsException('Failed to get the termination time of a proxy: ' + out)

        try:
            timeleft = min([int(v) for v in out.split('\n') if v])
            return datetime.utcnow() + timedelta(seconds = timeleft)
        except Exception, e:
            raise VomsException('Failed to get the termination time of a proxy: ' + str(e))
