import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .api.serializers import DietaEmEdicaoAbertaSerializer
from .models import DietaEmEdicaoAberta

logger = logging.getLogger()


class DietasEmEdicaoConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add('dietas_abertas', self.channel_name)
        await self.accept()

        dietas_em_edicao = await self.get_dietas_em_edicao()

        await self.send(text_data=json.dumps({
            'message': dietas_em_edicao
        }))

    @database_sync_to_async
    def get_dietas_em_edicao(self):
        return DietaEmEdicaoAbertaSerializer(DietaEmEdicaoAberta.objects.all(), many=True).data

    async def disconnect(self, code):
        await self.channel_layer.group_discard('dietas_abertas', self.channel_name)

    async def dieta_message(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def dispatch(self, message):
        """Created because when the ValueErrorException is raised the connection is broken."""
        try:
            return await super().dispatch(message)

        except ValueError as exception:
            logger.error(exception)
