from rest_framework import serializers

from sme_terceirizadas.dados_comuns.utils import update_instance_from_dict
from sme_terceirizadas.pre_recebimento.models import FichaTecnicaDoProduto
from sme_terceirizadas.pre_recebimento.models.cronograma import EtapasDoCronograma
from sme_terceirizadas.recebimento.models import (
    FichaDeRecebimento,
    QuestaoConferencia,
    QuestoesPorProduto,
    VeiculoFichaDeRecebimento,
)


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

    def update(self, instance, validated_data):
        instance.questoes_primarias.clear()
        instance.questoes_secundarias.clear()

        instance.questoes_primarias.set(validated_data.pop("questoes_primarias", []))
        instance.questoes_secundarias.set(
            validated_data.pop("questoes_secundarias", [])
        )

        return instance

    class Meta:
        model = QuestoesPorProduto
        fields = ("ficha_tecnica", "questoes_primarias", "questoes_secundarias")


class VeiculoFichaDeRecebimentoRascunhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VeiculoFichaDeRecebimento
        exclude = ("id", "ficha_recebimento")


class FichaDeRecebimentoRascunhoSerializer(serializers.ModelSerializer):
    etapa = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        queryset=EtapasDoCronograma.objects.all(),
    )
    veiculos = VeiculoFichaDeRecebimentoRascunhoSerializer(many=True)

    def create(self, validated_data):
        dados_veiculos = validated_data.pop("veiculos")
        instance = FichaDeRecebimento.objects.create(**validated_data)

        self._cria_veiculos(instance, dados_veiculos)

        return instance

    def update(self, instance, validated_data):
        instance.veiculos.all().delete()
        dados_veiculos = validated_data.pop("veiculos")

        instance = update_instance_from_dict(instance, validated_data, save=True)

        self._cria_veiculos(instance, dados_veiculos)

        return instance

    def _cria_veiculos(self, instance, dados_veiculos):
        for dados_veiculo in dados_veiculos:
            VeiculoFichaDeRecebimento.objects.create(
                ficha_recebimento=instance,
                **dados_veiculo,
            )

    class Meta:
        model = FichaDeRecebimento
        exclude = ("id",)
