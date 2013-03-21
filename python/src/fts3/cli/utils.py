import json


def job2HumanReadable(job):
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



def jobList2HumanReadable(jobList):
	"""
	Generates a guman readable string for the given job list.
	"""
	jobStr = []
	for job in jobList:
		jobStr.append(job2HumanReadable(job))
	return '\n'.join(jobStr)
	


def jobList2Json(job):
	"""
	Serializes a job list into JSON
	"""
	return json.dumps(job, indent = 2)



def job2Json(job):
	"""
	Serializes a job into JSON
	"""
	return json.dumps(job, indent = 2)
