#   Copyright notice:
#   Copyright CERN, 2014.
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

from fts3.rest.client import Inquirer


def list_jobs(context, user_dn=None, vo=None, source_se=None, dest_se=None, delegation_id=None, state_in=None):
    """
    List active jobs. Can filter by user_dn and vo

    Args:
        context:       fts3.rest.client.context.Context instance
        user_dn:       Filter by user dn. Can be left empty
        vo:            Filter by vo. Can be left empty
        delegation_id: Filter by delegation ID. Mandatory for state_in
        state_in:      Filter by job state. An iterable is expected (i.e. ['SUBMITTED', 'ACTIVE']

    Returns:
        Decoded JSON message returned by the server (list of jobs)
    """
    inquirer = Inquirer(context)
    return inquirer.get_job_list(user_dn, vo, source_se, dest_se, delegation_id, state_in)


def get_job_status(context, job_id, list_files=False):
    """
    Get a job status

    Args:
        context:    fts3.rest.client.context.Context instance
        job_id:     The job ID
        list_files: If True, the status of each individual file will be queried

    Returns:
        Decoded JSON message returned by the server (job status plus, optionally, list of files)
    """
    inquirer = Inquirer(context)
    return inquirer.get_job_status(job_id, list_files)

def get_jobs_statuses(context, job_ids, list_files=False):
    """
    Get status for a list of jobs

    Args:
        context:    fts3.rest.client.context.Context instance
        job_ids:    The job list
        list_files: If True, the status of each individual file will be queried

    Returns:
        Decoded JSON message returned by the server (job status plus, optionally, list of files)
    """
    inquirer = Inquirer(context)
    return inquirer.get_jobs_statuses(job_ids, list_files)
