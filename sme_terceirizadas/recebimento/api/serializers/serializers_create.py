from rest_framework import serializers

from sme_terceirizadas.pre_recebimento.models import FichaTecnicaDoProduto
from sme_terceirizadas.recebimento.models import QuestaoConferencia, QuestoesPorProduto


class QuestoesPorProdutoCreateSerializer(serializers.ModelSerializer):
    ficha_tecnica = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=FichaTecnicaDoProduto.objects.all(),
    )
    questoes_primarias = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=QuestaoConferencia.objects.all(),
        many=True,
    )
    questoes_secundarias = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=QuestaoConferencia.objects.all(),
        many=True,
    )

    def create(self, validated_data):
        questoes_primarias = validated_data.pop("questoes_primarias", [])
        questoes_secundarias = validated_data.pop("questoes_secundarias", [])

        instance = super().create(validated_data)
        instance.questoes_primarias.set(questoes_primarias)
        instance.questoes_secundarias.set(questoes_secundarias)

        return instance

    class Meta:
        model = QuestoesPorProduto
        fields = ("ficha_tecnica", "questoes_primarias", "questoes_secundarias")
