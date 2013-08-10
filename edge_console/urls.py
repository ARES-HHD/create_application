# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from edge_console.views import *


urlpatterns += patterns(
    'edge_console.views',

    url(r'^create_username/$', create_username),
    )
