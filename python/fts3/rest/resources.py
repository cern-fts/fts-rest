from django.conf import settings
from django.conf.urls.defaults import url
from fts3 import orm
from tastyalchemy import SQLAlchemyResource
from tastypie.resources import ALL, ModelResource
import threading

@staticmethod
def sessionMaker(x):
	local = threading.local()
	if not hasattr(local, 'session'):
		local.session = orm.connect(settings.FTS3_ORM_CONNECT_STRING)
	return local.session 



class JobResource(SQLAlchemyResource):
	
	class Meta:
		resource_name   = 'job'
		object_class    = orm.Job
		allowed_methods = ['get']
		key_field       = 'job_id'
		order_by        = '-submit_time'
		
		session_maker = sessionMaker
		
	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/files/$" % self._meta.resource_name,
			    self.wrap_view('get_transfers'), name="api_dispatch_transfers"),
		]
		
	def get_transfers(self, request, **kwargs):
		try:
			obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
		except ObjectDoesNotExist():
			raise HttpGone()
		except MultipleObjectsReturned:
			raise HttpMultipleChoices()
		transfers = FileResource()
		return transfers.get_list(request, job_id = obj.job_id)



class FileResource(SQLAlchemyResource):
	
	class Meta:
		resource_name   = 'file'
		object_class    = orm.File
		allowed_methods = ['get']
		key_field       = 'file_id'
		order_by        = '-file_id'
		
		session_maker   = sessionMaker



class ConfigAuditResource(SQLAlchemyResource):
	
	class Meta:
		resource_name   = 'audit'
		object_class    = orm.ConfigAudit
		allowed_methods = ['get']
		
		session_maker   = sessionMaker



class LinkResource(SQLAlchemyResource):
	
	class Meta:
		resource_name   = 'link'
		object_class    = orm.LinkConfig
		allowed_methods = ['get']
		
		session_maker   = sessionMaker
	


class SeResource(SQLAlchemyResource):
	
	class Meta:
		resource_name   = 'se'
		object_class    = orm.Se
		allowed_methods = ['get']
		key_field       = 'name'
		
		session_maker   = sessionMaker
		


class ShareResource(SQLAlchemyResource):
	
	class Meta:
		resource_name   = 'share'
		object_class    = orm.ShareConfig
		allowed_methods = ['get']
		
		session_maker   = sessionMaker



class MemberResource(SQLAlchemyResource):
	class Meta:
		resource_name   = 'group'
		object_class    = orm.Member
		allowed_methods = ['get']
		key_field       = 'groupname'
		
		session_maker   = sessionMaker
