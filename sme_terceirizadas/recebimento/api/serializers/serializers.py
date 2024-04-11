from rest_framework import serializers

from ...models import QuestaoConferencia, QuestoesPorProduto


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


class QuestoesPorProdutoSerializer(serializers.ModelSerializer):
    numero_ficha = serializers.SerializerMethodField()
    nome_produto = serializers.SerializerMethodField()
    questoes_primarias = serializers.SerializerMethodField()
    questoes_secundarias = serializers.SerializerMethodField()

    def get_numero_ficha(self, obj):
        return obj.ficha_tecnica.numero if obj.ficha_tecnica else None

    def get_nome_produto(self, obj):
        return obj.ficha_tecnica.produto.nome if obj.ficha_tecnica else None

    def get_questoes_primarias(self, obj):
        return (
            obj.questoes_primarias.all().values_list("questao", flat=True)
            if obj.questoes_primarias
            else []
        )

    def get_questoes_secundarias(self, obj):
        return (
            obj.questoes_secundarias.all().values_list("questao", flat=True)
            if obj.questoes_secundarias
            else []
        )

    class Meta:
        model = QuestoesPorProduto
        fields = (
            "uuid",
            "numero_ficha",
            "nome_produto",
            "questoes_primarias",
            "questoes_secundarias",
        )
