from rest_framework import serializers

from ...models import QuestaoConferencia


class QuestaoConferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestaoConferencia
        fields = (
            "uuid",
            "questao",
            "tipo_questao",
            "pergunta_obrigatoria",
            "posicao",
        )


class QuestaoConferenciaSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestaoConferencia
        fields = (
            "uuid",
            "questao",
        )
