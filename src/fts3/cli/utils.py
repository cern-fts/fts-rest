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

try:
    import simplejson as json
except:
    import json 


def job_human_readable(job):
    """
    Generates a human readable string for the given job.
    """

    s = """Request ID: %(job_id)s
Status: %(job_state)s
Client DN: %(user_dn)s
Reason: %(reason)s
Submission time: %(submit_time)s
Priority: %(priority)d
VO Name: %(vo_name)s
""" % job

    return s


def job_list_human_readable(job_list):
    """
    Generates a guman readable string for the given job list.
    """
    jobstr = []
    for job in job_list:
        jobstr.append(job_human_readable(job))
    return '\n'.join(jobstr)


def job_list_as_json(job_list):
    """
    Serializes a job list into JSON
    """
    return json.dumps(job_list, indent=2)


def job_as_json(job):
    """
    Serializes a job into JSON
    """
    return json.dumps(job, indent=2)
