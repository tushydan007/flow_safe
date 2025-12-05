"""
WebSocket routing for pipeline app.
"""

from django.urls import re_path

from .consumers import PipelineConsumer, AlertConsumer

websocket_urlpatterns = [
    re_path(r'ws/pipeline/$', PipelineConsumer.as_asgi()),
    re_path(r'ws/alerts/$', AlertConsumer.as_asgi()),
]

