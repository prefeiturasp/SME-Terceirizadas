from rest_framework import serializers

from ....dados_comuns.utils import update_instance_from_dict
from ....dados_comuns.validators import (
    campo_deve_ser_deste_tipo,
    campo_nao_pode_ser_nulo,
    deve_pedir_com_antecedencia,
    nao_pode_ser_no_passado
)
from ....escola.models import DiretoriaRegional, Escola
from ...models import (
    EscolaQuantidade,
    KitLanche,
    SolicitacaoKitLanche,
    SolicitacaoKitLancheAvulsa,
    SolicitacaoKitLancheUnificada
)
from ..validators import (
    escola_quantidade_deve_ter_1_ou_mais_kits,
    escola_quantidade_nao_deve_ter_kits_e_tempo_passeio,
    escola_quantidade_pedido_nao_pode_ser_mais_que_alunos,
    solicitacao_deve_ter_0_kit,
    solicitacao_deve_ter_1_ou_mais_kits,
    valida_quantidade_kits_tempo_passeio,
    valida_tempo_passeio_lista_igual,
    valida_tempo_passeio_lista_nao_igual
)


class SolicitacaoKitLancheCreationSerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        slug_field='uuid', many=True,
        required=True,
        queryset=KitLanche.objects.all())
    tempo_passeio_explicacao = serializers.CharField(
        source='get_tempo_passeio_display',
        required=False,
        read_only=True)

    def validate_data(self, data):
        nao_pode_ser_no_passado(data)
        deve_pedir_com_antecedencia(data)
        return data

    def validate(self, attrs):
        tempo_passeio = attrs.get('tempo_passeio')
        qtd_kits = len(attrs.get('kits'))
        valida_quantidade_kits_tempo_passeio(tempo_passeio, qtd_kits)
        return attrs

    def create(self, validated_data):
        kits = validated_data.pop('kits', [])
        solicitacao_kit_lanche = SolicitacaoKitLanche.objects.create(**validated_data)
        solicitacao_kit_lanche.kits.set(kits)
        return solicitacao_kit_lanche

    def update(self, instance, validated_data):
        kits = validated_data.pop('kits', [])
        update_instance_from_dict(instance, validated_data)
        instance.kits.set(kits)
        instance.save()

        return instance

    class Meta:
        model = SolicitacaoKitLanche
        exclude = ('id',)


class SolicitacaoKitLancheAvulsaCreationSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheCreationSerializer(
        required=True
    )
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Escola.objects.all()
    )

    status_explicacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )

    def validate(self, attrs):
        quantidade_aluno_passeio = attrs.get('quantidade_alunos')
        data_evento = attrs.get('solicitacao_kit_lanche').get('data')
        campo_nao_pode_ser_nulo(quantidade_aluno_passeio, mensagem='O campo Quantidade de aluno não pode ser nulo')
        campo_deve_ser_deste_tipo(quantidade_aluno_passeio, tipo=int, mensagem='Quantidade de aluno de ser do tipo int')
        nao_pode_ser_no_passado(data_evento)
        deve_pedir_com_antecedencia(data_evento)
        return attrs

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        solicitacao_kit_lanche_json = validated_data.pop('solicitacao_kit_lanche')
        solicitacao_kit_lanche = SolicitacaoKitLancheCreationSerializer(
        ).create(solicitacao_kit_lanche_json)
        solicitacao_kit_avulsa = SolicitacaoKitLancheAvulsa.objects.create(
            solicitacao_kit_lanche=solicitacao_kit_lanche, **validated_data
        )
        solicitacao_kit_avulsa.save()
        return solicitacao_kit_avulsa

    def update(self, instance, validated_data):
        solicitacao_kit_lanche_json = validated_data.pop('solicitacao_kit_lanche')
        solicitacao_kit_lanche = instance.solicitacao_kit_lanche

        SolicitacaoKitLancheCreationSerializer(
        ).update(solicitacao_kit_lanche, solicitacao_kit_lanche_json)

        update_instance_from_dict(instance, validated_data)

        instance.save()
        return instance

    class Meta:
        model = SolicitacaoKitLancheAvulsa
        exclude = ('id', 'status')


class EscolaQuantidadeCreationSerializer(serializers.ModelSerializer):
    kits = serializers.SlugRelatedField(
        slug_field='uuid', many=True,
        required=True,
        queryset=KitLanche.objects.all())
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Escola.objects.all()
    )

    tempo_passeio_explicacao = serializers.CharField(
        source='get_tempo_passeio_display',
        required=False,
        read_only=True)

    solicitacao_unificada = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=SolicitacaoKitLancheUnificada.objects.all()
    )

    def validate(self, attrs):
        qtd_kits = len(attrs.get('kits'))
        tempo_passeio = attrs.get('tempo_passeio')
        valida_quantidade_kits_tempo_passeio(tempo_passeio, qtd_kits)
        return attrs

    def create(self, validated_data):
        kits = validated_data.pop('kits', [])
        escola_quantiade = EscolaQuantidade.objects.create(**validated_data)
        escola_quantiade.kits.set(kits)
        return escola_quantiade

    def update(self, instance, validated_data):
        kits = validated_data.pop('kits', [])
        update_instance_from_dict(instance, validated_data)
        instance.kits.set(kits)
        instance.save()
        return instance

    class Meta:
        model = EscolaQuantidade
        exclude = ('id',)


class SolicitacaoKitLancheUnificadaCreationSerializer(serializers.ModelSerializer):
    solicitacao_kit_lanche = SolicitacaoKitLancheCreationSerializer(
        required=False
    )
    diretoria_regional = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=DiretoriaRegional.objects.all()
    )
    escolas_quantidades = EscolaQuantidadeCreationSerializer(
        many=True,
        required=False
    )
    status_explicacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )

    def create(self, validated_data):
        lista_igual = validated_data.get('lista_kit_lanche_igual', True)
        solicitacao_kit_lanche = validated_data.pop('solicitacao_kit_lanche')
        escolas_quantidades = validated_data.pop('escolas_quantidades')
        validated_data['criado_por'] = self.context['request'].user

        solicitacao_base = SolicitacaoKitLancheCreationSerializer().create(solicitacao_kit_lanche)

        if not lista_igual:
            solicitacao_base.kits.set([])

        lista_quantidade_escola = self._gera_escolas_quantidades(escolas_quantidades)

        solicitacao_kit_unificada = SolicitacaoKitLancheUnificada.objects.create(
            solicitacao_kit_lanche=solicitacao_base, **validated_data
        )

        solicitacao_kit_unificada.escolas_quantidades.set(lista_quantidade_escola)
        return solicitacao_kit_unificada

    def update(self, instance, validated_data):
        lista_igual = validated_data.get('lista_kit_lanche_igual', True)
        escolas_quantidades = validated_data.pop('escolas_quantidades')
        solicitacao_kit_lanche_json = validated_data.pop('solicitacao_kit_lanche')

        solicitacao_kit_lanche = instance.solicitacao_kit_lanche
        instance.escolas_quantidades.all().delete()

        if not lista_igual:
            solicitacao_kit_lanche.kits.set([])

        SolicitacaoKitLancheCreationSerializer().update(solicitacao_kit_lanche, solicitacao_kit_lanche_json)

        lista_quantidade_escola = self._gera_escolas_quantidades(escolas_quantidades)

        instance.escolas_quantidades.set(lista_quantidade_escola)

        update_instance_from_dict(instance, validated_data)
        instance.save()
        return instance

    def validate(self, data):

        self._valida_dados_base(data)
        self._valida_escolas_quantidades(data)

        return data

    def _valida_dados_base(self, data):
        solicitacao_kit_lanche = data.get('solicitacao_kit_lanche')
        kits_base = solicitacao_kit_lanche.get('kits', [])
        lista_igual = data.get('lista_kit_lanche_igual', True)
        tempo_passeio_base = solicitacao_kit_lanche.get('tempo_passeio', None)

        if lista_igual:
            valida_tempo_passeio_lista_igual(tempo_passeio_base)
            solicitacao_deve_ter_1_ou_mais_kits(len(kits_base))
        else:
            valida_tempo_passeio_lista_nao_igual(tempo_passeio_base)
            solicitacao_deve_ter_0_kit(len(kits_base))

    def _valida_escolas_quantidades(self, data):
        escolas_quantidades = data.get('escolas_quantidades')
        lista_igual = data.get('lista_kit_lanche_igual', True)

        if lista_igual:
            cont = 0
            for escola_quantidade in escolas_quantidades:
                kits = escola_quantidade.get('kits')
                escola_quantidade_nao_deve_ter_kits_e_tempo_passeio(
                    num_kits=len(kits),
                    tempo_passeio=escola_quantidade.get('tempo_passeio'),
                    indice=cont
                )
                escola_quantidade_pedido_nao_pode_ser_mais_que_alunos(
                    escola=escola_quantidade.get('escola'),
                    quantidade_alunos_pedido=escola_quantidade.get('quantidade_alunos'),
                    indice=cont
                )
                cont += 1
        else:
            cont = 0
            for escola_quantidade in escolas_quantidades:
                kits = escola_quantidade.get('kits')
                escola_quantidade_deve_ter_1_ou_mais_kits(len(kits), indice=cont)
                cont += 1

    def _gera_escolas_quantidades(self, escolas_quantidades):
        escola_quantidade_lista = []
        for escola_quantidade_json in escolas_quantidades:
            escola_quantidade_object = EscolaQuantidadeCreationSerializer(
            ).create(escola_quantidade_json)
            escola_quantidade_lista.append(escola_quantidade_object)
        return escola_quantidade_lista

    def _atualiza_escolas_quantidades(self, escolas_quantidades, escolas_quantidades_lista):
        # TODO: quando o o len dos dois for diferente, tratar esse diff...
        for index in range(len(escolas_quantidades)):
            EscolaQuantidadeCreationSerializer(
            ).update(instance=escolas_quantidades[index],
                     validated_data=escolas_quantidades_lista[index])

    class Meta:
        model = SolicitacaoKitLancheUnificada
        exclude = ('id', 'status')
