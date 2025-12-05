"""
WebSocket consumers for real-time updates.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class PipelineConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for pipeline updates.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        user = self.scope.get('user')
        if user and user.is_authenticated:
            self.organization_id = await self.get_organization_id(user)
            if self.organization_id:
                self.room_group_name = f'pipeline_{self.organization_id}'
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connection is alive'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def pipeline_update(self, event):
        """Send pipeline update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'pipeline_update',
            'data': event['data']
        }))

    async def image_update(self, event):
        """Send satellite image update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'image_update',
            'data': event['data']
        }))

    async def analysis_progress(self, event):
        """Send analysis progress update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'analysis_progress',
            'data': event['data']
        }))

    async def analysis_complete(self, event):
        """Send analysis completion notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'analysis_complete',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_organization_id(self, user):
        """Get the organization ID for the user."""
        try:
            return user.organization.pk
        except Exception:
            return None


class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for alert notifications.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        user = self.scope.get('user')
        if user and user.is_authenticated:
            self.organization_id = await self.get_organization_id(user)
            if self.organization_id:
                self.room_group_name = f'alerts_{self.organization_id}'
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connection is alive'
                }))
            elif message_type == 'acknowledge':
                alert_id = data.get('alert_id')
                if alert_id:
                    await self.send(text_data=json.dumps({
                        'type': 'alert_acknowledged',
                        'alert_id': alert_id
                    }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def new_alert(self, event):
        """Send new alert notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'new_alert',
            'data': event['data']
        }))

    async def alert_update(self, event):
        """Send alert update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'alert_update',
            'data': event['data']
        }))

    async def critical_alert(self, event):
        """Send critical alert that triggers sound notification."""
        await self.send(text_data=json.dumps({
            'type': 'critical_alert',
            'data': event['data'],
            'sound': True
        }))

    @database_sync_to_async
    def get_organization_id(self, user):
        """Get the organization ID for the user."""
        try:
            return user.organization.pk
        except Exception:
            return None

