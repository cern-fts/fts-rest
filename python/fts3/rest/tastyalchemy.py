# Adapted from
# https://github.com/devhub/tastyalchemy

from sqlalchemy import (Boolean, Date, DateTime, Integer,
                        String, Unicode, UnicodeText)
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import Resource

FIELD_MAP = {
    Boolean: fields.BooleanField,
    Date: fields.DateField,
    DateTime: fields.DateTimeField,
    Integer: fields.IntegerField,
    String: fields.CharField,
    Unicode: fields.CharField,
    UnicodeText: fields.CharField,
}


class SQLAlchemyResource(Resource):
	
    def __init__(self, api_name=None):
        super(SQLAlchemyResource, self).__init__(api_name)
        for col in self._meta.object_class.__table__.columns:
            if col.name not in self._meta.excludes:
                kwargs = {
                    'attribute': col.name,
                    'null': col.nullable,
                }
                self.fields[col.name] = FIELD_MAP.get(col.type.__class__,
                    fields.CharField)(**kwargs)

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle) and hasattr(self._meta, 'key_field'):
            kwargs['pk'] = getattr(bundle_or_obj.obj, self._meta.key_field)

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def get_object_list(self, request):
        sess = self._meta.session_maker()
        results = []
        for obj in sess.query(self._meta.object_class).all():
            results.append(obj)
        return results

    def obj_get_list(self, request=None, **kwargs):
        return self.get_object_list(request)

    def obj_get(self, request=None, **kwargs):
        sess = self._meta.session_maker()
        obj = sess.query(self._meta.object_class).get(kwargs['pk'])
        if not obj:
            raise NotFound('%s not found' % self._meta.resource_name)
        return obj

    def obj_create(self, bundle, request=None, **kwargs):
        sess = self._meta.session_maker()
        bundle.obj = self._meta.object_class()
        bundle.obj.update(bundle.data)
        sess.add(bundle.obj)
        sess.commit()
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        sess = self._meta.session_maker()
        obj = sess.query(self._meta.object_class).get(kwargs['pk'])
        obj.update(bundle.data)
        sess.commit()
        return bundle
    
    #def obj_delete_list(self, request=None, **kwargs):
    #    pass # TODO

    def obj_delete(self, request=None, **kwargs):
        sess = self._meta.session_maker()
        obj = sess.query(self._meta.object_class).get(kwargs['pk'])
        sess.delete(obj)
        sess.commit()
