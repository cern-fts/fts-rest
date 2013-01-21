from django.conf.urls import patterns, include, url
import fts3.rest.urls

urlpatterns = patterns('',
    url(r'^api/', include(fts3.rest.urls.urlpatterns))
)
