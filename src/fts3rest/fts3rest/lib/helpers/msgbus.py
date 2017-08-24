#   Copyright notice:
#   Copyright CERN, 2016.
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

import os
import pylons
import socket
import tempfile
import time
from dirq.QueueSimple import QueueSimple

try:
    import simplejson as json
except:
    import json

def submit_state_change(job, transfer):
    """
    Writes a state change message to the dirq
    """
    msg_dir = pylons.config.get('fts3.MessagingDirectory', '/var/lib/fts3')
    mon_dir = os.path.join(msg_dir, 'monitoring')

    msg = dict(
        endpnt = pylons.config['fts3.Alias'],
        user_dn=job['user_dn'],
        src_url=transfer['source_surl'],
        dst_url=transfer['dest_surl'],
        vo_name=job['vo_name'],
        source_se=transfer['source_se'],
        dest_se=transfer['dest_se'],
        job_id=job['job_id'],
        file_id=transfer['file_id'],
        job_state=job['job_state'],
        file_state=transfer['file_state'],
        retry_counter=0,
        retry_max=0,
        timestamp=time.time()*1000,
        job_metadata=job['job_metadata'],
        file_metadata=transfer['file_metadata'],
    )

    tmpfile = tempfile.NamedTemporaryFile(dir=msg_dir, delete=False)
    tmpfile.write("SS ")
    json.dump(msg, tmpfile)
    tmpfile.close()

    q = QueueSimple(path=mon_dir)
    q.add_path(tmpfile.name)
