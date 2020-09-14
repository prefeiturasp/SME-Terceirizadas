from datetime import datetime

from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from ...dados_comuns.api.serializers import ContatoSerializer, LogSolicitacoesUsuarioSerializer
from ...dados_comuns.utils import update_instance_from_dict
from ...dados_comuns.validators import nao_pode_ser_no_passado
from ...escola.api.serializers import AlunoSerializer, LoteNomeSerializer, TipoGestaoSerializer
from ...escola.models import DiretoriaRegional, Escola
from ...produto.api.serializers.serializers import ProdutoSimplesSerializer
from ...produto.models import SolicitacaoCadastroProdutoDieta
from ..models import (
    AlergiaIntolerancia,
    Alimento,
    Anexo,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    SubstituicaoAlimento
)
from .serializers_create import SolicitacaoDietaEspecialCreateSerializer, SubstituicaoAlimentoCreateSerializer
from .validators import atributos_lista_nao_vazios, atributos_string_nao_vazios, deve_ter_atributos


class AlergiaIntoleranciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlergiaIntolerancia
        fields = '__all__'


class ClassificacaoDietaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificacaoDieta
        fields = '__all__'


class MotivoNegacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoNegacao
        fields = '__all__'


class AlimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimento
        fields = '__all__'


class AnexoSerializer(ModelSerializer):
    nome = serializers.CharField()

    class Meta:
        model = Anexo
        fields = ('arquivo', 'nome', 'eh_laudo_alta')


class SubstituicaoAlimentoSerializer(ModelSerializer):
    alimento = AlimentoSerializer()
    substitutos = ProdutoSimplesSerializer(many=True)

    class Meta:
        model = SubstituicaoAlimento
        fields = '__all__'


class SolicitacaoDietaEspecialAutorizarSerializer(SolicitacaoDietaEspecialCreateSerializer):
    def validate(self, dados_a_validar):
        deve_ter_atributos(
            dados_a_validar,
            [
                'alergias_intolerancias',
                'classificacao',
                'registro_funcional_nutricionista',
                'substituicoes'
            ]
        )
        if 'data_termino' in dados_a_validar:
            data_termino = datetime.strptime(dados_a_validar['data_termino'], '%Y-%m-%d').date()
            nao_pode_ser_no_passado(data_termino)
        atributos_lista_nao_vazios(dados_a_validar, ['substituicoes', 'alergias_intolerancias'])
        atributos_string_nao_vazios(dados_a_validar, ['registro_funcional_nutricionista'])
        return dados_a_validar

    def update(self, instance, data):
        validated_data = self.validate(data)
        alergias_intolerancias = validated_data.pop('alergias_intolerancias')
        substituicoes = validated_data.pop('substituicoes')

        instance.classificacao_id = validated_data['classificacao']
        instance.registro_funcional_nutricionista = validated_data['registro_funcional_nutricionista']
        instance.informacoes_adicionais = validated_data.get('informacoes_adicionais', '')
        instance.nome_protocolo = validated_data.get('nome_protocolo', '')
        data_termino = validated_data.get('data_termino', '')
        if data_termino:
            instance.data_termino = data_termino
        instance.ativo = True

        instance.alergias_intolerancias.all().delete()
        for ai in alergias_intolerancias:
            instance.alergias_intolerancias.add(AlergiaIntolerancia.objects.get(pk=ai))

        instance.substituicaoalimento_set.all().delete()
        for substituicao in substituicoes:
            substituicao['solicitacao_dieta_especial'] = instance.id
            ser = SubstituicaoAlimentoCreateSerializer(data=substituicao)
            ser.is_valid(raise_exception=True)
            instance.substituicaoalimento_set.add(ser.save())

        return instance


class DiretoriaRegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiretoriaRegional
        fields = ['nome', 'codigo_eol']


class EscolaSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSerializer()
    tipo_gestao = TipoGestaoSerializer()
    lote = LoteNomeSerializer()
    contato = ContatoSerializer()

    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'diretoria_regional', 'tipo_gestao', 'lote', 'contato')


class SolicitacaoDietaEspecialSerializer(serializers.ModelSerializer):
    aluno = AlunoSerializer()
    anexos = serializers.ListField(
        child=AnexoSerializer(), required=True
    )
    escola = EscolaSerializer()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    status_solicitacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )
    id_externo = serializers.CharField()

    classificacao = ClassificacaoDietaSerializer()
    alergias_intolerancias = AlergiaIntoleranciaSerializer(many=True)
    motivo_negacao = MotivoNegacaoSerializer()

    substituicoes = SubstituicaoAlimentoSerializer(many=True)

    tem_solicitacao_cadastro_produto = serializers.SerializerMethodField()

    def get_tem_solicitacao_cadastro_produto(self, obj):
        return SolicitacaoCadastroProdutoDieta.objects.filter(solicitacao_dieta_especial=obj,
                                                              status='AGUARDANDO_CONFIRMACAO').exists()

    class Meta:
        model = SolicitacaoDietaEspecial
        ordering = ('ativo', '-criado_em')
        fields = (
            'uuid',
            'id_externo',
            'criado_em',
            'status_solicitacao',
            'aluno',
            'escola',
            'anexos',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'observacoes',
            'alergias_intolerancias',
            'classificacao',
            'nome_protocolo',
            'substituicoes',
            'informacoes_adicionais',
            'motivo_negacao',
            'justificativa_negacao',
            'registro_funcional_nutricionista',
            'logs',
            'ativo',
            'data_termino',
            'tem_solicitacao_cadastro_produto'
        )


class SolicitacaoDietaEspecialUpdateSerializer(serializers.ModelSerializer):
    anexos = serializers.ListField(
        child=AnexoSerializer(), required=True
    )

    classificacao = serializers.PrimaryKeyRelatedField(queryset=ClassificacaoDieta.objects.all())
    alergias_intolerancias = serializers.PrimaryKeyRelatedField(queryset=AlergiaIntolerancia.objects.all(), many=True)

    substituicoes = SubstituicaoAlimentoCreateSerializer(many=True)

    def update(self, instance, data):  # noqa C901
        anexos = data.pop('anexos', [])
        alergias_intolerancias = data.pop('alergias_intolerancias', None)
        substituicoes = data.pop('substituicoes', None)

        update_instance_from_dict(instance, data)

        if anexos:
            instance.anexo_set.all().delete()
            for anexo in anexos:
                anexo['solicitacao_dieta_especial_id'] = instance.id
                ser = AnexoSerializer(data=anexo)
                ser.is_valid(raise_exception=True)
                Anexo.objects.create(**anexo)

        if alergias_intolerancias:
            instance.alergias_intolerancias.set([])
            for ai in alergias_intolerancias:
                instance.alergias_intolerancias.add(ai)

        if substituicoes:
            instance.substituicaoalimento_set.all().delete()
            for substituicao in substituicoes:
                substitutos = substituicao.pop('substitutos', None)
                substituicao['solicitacao_dieta_especial'] = instance
                subst_obj = SubstituicaoAlimento.objects.create(**substituicao)
                if substitutos:
                    subst_obj.substitutos.set(substitutos)

        instance.save()
        return instance

    class Meta:
        model = SolicitacaoDietaEspecial
        exclude = ('id',)


class SolicitacaoDietaEspecialLogSerializer(serializers.ModelSerializer):
    aluno = AlunoSerializer()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    id_externo = serializers.CharField()

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = ('uuid', 'aluno', 'logs', 'id_externo')


class SolicitacoesAtivasInativasPorAlunoSerializer(serializers.Serializer):
    dre = serializers.CharField(source='aluno.escola.diretoria_regional.nome')
    escola = serializers.CharField(source='aluno.escola.nome')
    codigo_eol = serializers.CharField(source='aluno.codigo_eol')
    nome = serializers.CharField(source='aluno.nome')
    ativas = serializers.IntegerField()
    inativas = serializers.IntegerField()


class RelatorioQuantitativoSolicDietaEspSerializer(serializers.Serializer):
    dre = serializers.CharField(source='aluno__escola__diretoria_regional__nome', required=False)
    escola = serializers.CharField(source='aluno__escola__nome', required=False)
    qtde_ativas = serializers.IntegerField()
    qtde_inativas = serializers.IntegerField()
    qtde_pendentes = serializers.IntegerField()
