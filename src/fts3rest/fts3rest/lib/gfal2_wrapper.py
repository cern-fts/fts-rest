#   Copyright notice:
#   Copyright © Members of the EMI Collaboration, 2010.
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

import errno
import json
import os
import signal
from StringIO import StringIO

import gfal2


context_type = gfal2.creat_context


class Gfal2Error(Exception):
    """
    Controlled error from gfal2
    """
    def __init__(self, errno, message):
        self.errno = errno
        self.message = message


class Gfal2Wrapper(object):
    """
    Wraps the calls to gfal2 in a separated process.
    This reduces the risks of bugs from gfal2, or bad isolation
    impacting the REST API (i.e FTS-35)
    """

    def __init__(self, proxy, method):
        """
        Calls method in a new process, with the environment properly set up, and a
        gfal2 context already initialized
        """
        self.proxy = proxy
        self.method = method

    def __call__(self, *args, **kwargs):
        pipe_read, pipe_write = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(pipe_read)
            self._child(os.fdopen(pipe_write, 'w'), args, kwargs)
            assert(False)
        else:
            os.close(pipe_write)
            return self._parent(pid, os.fdopen(pipe_read, 'r'))

    def _parent(self, child_pid, pipe):
        child_output = StringIO()
        out = pipe.read()
        while out:
            child_output.write(out)
            out = pipe.read()
        child_pid, child_status = os.waitpid(child_pid, os.P_WAIT)
        if os.WIFSIGNALED(child_status):
            child_signal = os.WTERMSIG(child_status)
            if child_signal == signal.SIGALRM:
                raise Gfal2Error(errno.ETIMEDOUT, 'Timeout expired')
            else:
                raise Gfal2Error(errno.EIO, 'Child process killed by signal %d' % child_signal)
        child_exit = os.WEXITSTATUS(child_status)
        if child_exit:
            raise Gfal2Error(child_exit, child_output.getvalue())
        return json.loads(child_output.getvalue())

    def _child(self, pipe, args, kwargs):
        signal.alarm(30)

        os.environ['X509_USER_CERT'] = self.proxy.name
        os.environ['X509_USER_KEY'] = self.proxy.name
        os.environ['X509_USER_PROXY'] = self.proxy.name
        exit_code = 0
        try:
            ctx = gfal2.creat_context()
            result = self.method(ctx, *args, **kwargs)
            pipe.write(json.dumps(result))
        except gfal2.GError, e:
            pipe.write(e.message)
            exit_code = e.code
        except Exception, e:
            pipe.write(e.message)
            exit_code = errno.EIO
        pipe.close()
        os._exit(exit_code)


__all__ = ['Gfal2Error', 'Gfal2Wrapper']
