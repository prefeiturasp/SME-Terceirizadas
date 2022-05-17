from datetime import datetime

import environ
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from ...dados_comuns.api.serializers import ContatoSerializer, LogSolicitacoesUsuarioSerializer
from ...dados_comuns.utils import update_instance_from_dict
from ...dados_comuns.validators import nao_pode_ser_no_passado
from ...escola.api.serializers import AlunoSerializer, LoteNomeSerializer, LoteSerializer, TipoGestaoSerializer
from ...escola.models import DiretoriaRegional, Escola
from ...produto.api.serializers.serializers import MarcaSimplesSerializer, ProdutoSimplesSerializer
from ...produto.models import Produto, SolicitacaoCadastroProdutoDieta
from ..models import (
    AlergiaIntolerancia,
    Alimento,
    Anexo,
    ClassificacaoDieta,
    MotivoAlteracaoUE,
    MotivoNegacao,
    ProtocoloPadraoDietaEspecial,
    SolicitacaoDietaEspecial,
    SubstituicaoAlimento,
    SubstituicaoAlimentoProtocoloPadrao,
    TipoContagem
)
from .serializers_create import (
    SolicitacaoDietaEspecialCreateSerializer,
    SubstituicaoAutorizarSerializer,
    SubstituicaoCreateSerializer
)
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
    marca = MarcaSimplesSerializer()

    class Meta:
        model = Alimento
        fields = '__all__'
        ordering = ('nome')


class AlimentosSubstitutosSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()

    def get_tipo(self, instance):
        return 'a'

    class Meta:
        model = Alimento
        fields = ('uuid', 'nome', 'tipo')


class TipoContagemSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoContagem
        exclude = ('id',)


class AnexoSerializer(ModelSerializer):
    nome = serializers.CharField()
    arquivo_url = serializers.SerializerMethodField()

    def get_arquivo_url(self, instance):
        env = environ.Env()
        api_url = env.str('URL_ANEXO', default='http://localhost:8000')
        return f'{api_url}{instance.arquivo.url}'

    class Meta:
        model = Anexo
        fields = ('arquivo_url', 'arquivo', 'nome', 'eh_laudo_alta')


class SubstituicaoAlimentoSerializer(ModelSerializer):
    alimento = AlimentoSerializer()
    substitutos = ProdutoSimplesSerializer(many=True)
    alimentos_substitutos = AlimentoSerializer(many=True)

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
            data_termino = datetime.strptime(
                dados_a_validar['data_termino'], '%Y-%m-%d').date()
            nao_pode_ser_no_passado(data_termino)
        atributos_lista_nao_vazios(
            dados_a_validar, ['substituicoes', 'alergias_intolerancias'])
        atributos_string_nao_vazios(
            dados_a_validar, ['registro_funcional_nutricionista'])
        return dados_a_validar

    def update(self, instance, data):  # noqa C901
        validated_data = self.validate(data)
        alergias_intolerancias = validated_data.pop('alergias_intolerancias')
        substituicoes = validated_data.pop('substituicoes')

        protocolo_padrao = ProtocoloPadraoDietaEspecial.objects.get(uuid=validated_data['protocolo_padrao'])
        instance.protocolo_padrao = protocolo_padrao

        instance.classificacao_id = validated_data['classificacao']
        instance.registro_funcional_nutricionista = validated_data['registro_funcional_nutricionista']
        instance.informacoes_adicionais = validated_data.get('informacoes_adicionais', '')
        instance.orientacoes_gerais = validated_data.get('orientacoes_gerais', '')
        instance.caracteristicas_do_alimento = validated_data.get('caracteristicas_do_alimento', '')
        instance.nome_protocolo = validated_data.get('nome_protocolo', '')
        data_termino = validated_data.get('data_termino', '')
        if data_termino:
            data_termino = datetime.strptime(data_termino, '%Y-%m-%d').date()
            instance.data_termino = data_termino

        instance.alergias_intolerancias.clear()

        for ai in alergias_intolerancias:
            instance.alergias_intolerancias.add(
                AlergiaIntolerancia.objects.get(pk=ai))

        instance.substituicaoalimento_set.all().delete()
        for substituicao in substituicoes:
            substituicao['solicitacao_dieta_especial'] = instance.id
            # Separa Alimentos e Produtos.
            alimentos_substitutos = []
            produtos_substitutos = []
            for substituto in substituicao['substitutos']:
                if Alimento.objects.filter(uuid=substituto).first():
                    alimentos_substitutos.append(substituto)
                elif Produto.objects.filter(uuid=substituto).first():
                    produtos_substitutos.append(substituto)
                else:
                    raise Exception('Substituto não encontrado.')

            substituicao['alimentos_substitutos'] = alimentos_substitutos
            substituicao['substitutos'] = produtos_substitutos

            create_serializer = SubstituicaoAutorizarSerializer(data=substituicao)  # noqa
            if create_serializer.is_valid(raise_exception=True):
                instance.substituicaoalimento_set.add(create_serializer.save())

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
        fields = ('uuid', 'nome', 'diretoria_regional',
                  'tipo_gestao', 'lote', 'contato')


class MotivoAlteracaoUESerializer(serializers.ModelSerializer):

    class Meta:
        model = MotivoAlteracaoUE
        fields = (
            'uuid',
            'nome',
            'descricao'
        )


class SolicitacaoDietaEspecialSerializer(serializers.ModelSerializer):
    aluno = AlunoSerializer()
    anexos = serializers.ListField(
        child=AnexoSerializer(), required=True
    )
    escola = EscolaSerializer()
    escola_destino = EscolaSerializer()
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
    motivo_alteracao_ue = MotivoAlteracaoUESerializer()
    substituicoes = serializers.SerializerMethodField()

    tem_solicitacao_cadastro_produto = serializers.SerializerMethodField()
    protocolo_padrao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ProtocoloPadraoDietaEspecial.objects.all()
    )

    def get_substituicoes(self, obj):
        substituicoes = obj.substituicoes.order_by('alimento__nome')
        return SubstituicaoAlimentoSerializer(substituicoes, many=True).data

    def get_tem_solicitacao_cadastro_produto(self, obj):
        return SolicitacaoCadastroProdutoDieta.objects.filter(
            solicitacao_dieta_especial=obj,
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
            'escola_destino',
            'anexos',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'observacoes',
            'alergias_intolerancias',
            'classificacao',
            'protocolo_padrao',
            'nome_protocolo',
            'orientacoes_gerais',
            'substituicoes',
            'informacoes_adicionais',
            'caracteristicas_do_alimento',
            'motivo_negacao',
            'justificativa_negacao',
            'registro_funcional_nutricionista',
            'logs',
            'ativo',
            'data_termino',
            'data_inicio',
            'tem_solicitacao_cadastro_produto',
            'tipo_solicitacao',
            'observacoes_alteracao',
            'motivo_alteracao_ue',
            'conferido',
            'eh_importado'
        )


class SolicitacaoDietaEspecialUpdateSerializer(serializers.ModelSerializer):
    protocolo_padrao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ProtocoloPadraoDietaEspecial.objects.all(),
        allow_null=True
    )
    anexos = serializers.ListField(child=AnexoSerializer(), required=True)
    classificacao = serializers.PrimaryKeyRelatedField(
        queryset=ClassificacaoDieta.objects.all()
    )
    alergias_intolerancias = serializers.PrimaryKeyRelatedField(
        queryset=AlergiaIntolerancia.objects.all(), many=True
    )
    substituicoes = SubstituicaoCreateSerializer(many=True)

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

        instance.substituicaoalimento_set.all().delete()
        if substituicoes:
            for substituicao in substituicoes:
                substitutos = substituicao.pop('substitutos', None)
                substituicao['solicitacao_dieta_especial'] = instance
                subst_obj = SubstituicaoAlimento.objects.create(**substituicao)
                if substitutos:
                    for substituto in substitutos:
                        if isinstance(substituto, Alimento):
                            subst_obj.alimentos_substitutos.add(substituto)
                        if isinstance(substituto, Produto):
                            subst_obj.substitutos.add(substituto)

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
    dre = serializers.CharField(source='escola.diretoria_regional.nome')
    escola = serializers.CharField(source='escola.nome')
    codigo_eol = serializers.CharField()
    uuid = serializers.CharField()
    nome = serializers.CharField()
    ativas = serializers.IntegerField()
    inativas = serializers.IntegerField()


class RelatorioQuantitativoSolicDietaEspSerializer(serializers.Serializer):
    dre = serializers.CharField(
        source='aluno__escola__diretoria_regional__nome', required=False)
    escola = serializers.CharField(
        source='aluno__escola__nome', required=False)
    diagnostico = serializers.CharField(
        source='alergias_intolerancias__descricao', required=False)
    classificacao = serializers.CharField(
        source='classificacao__nome', required=False)
    ano_nasc_aluno = serializers.CharField(
        source='aluno__data_nascimento__year', required=False)
    qtde_ativas = serializers.IntegerField()
    qtde_inativas = serializers.IntegerField()
    qtde_pendentes = serializers.IntegerField()


class SolicitacaoDietaEspecialSimplesSerializer(serializers.ModelSerializer):
    aluno = AlunoSerializer()
    rastro_escola = EscolaSerializer()
    status_titulo = serializers.CharField(source='status.state.title')
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    status_solicitacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )
    classificacao = ClassificacaoDietaSerializer()
    alergias_intolerancias = AlergiaIntoleranciaSerializer(many=True)
    motivo_negacao = MotivoNegacaoSerializer()
    anexos = serializers.ListField(
        child=AnexoSerializer(), required=True
    )

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'uuid',
            'id_externo',
            'criado_em',
            'status_solicitacao',
            'aluno',
            'rastro_escola',
            'alergias_intolerancias',
            'classificacao',
            'nome_protocolo',
            'motivo_negacao',
            'justificativa_negacao',
            'registro_funcional_nutricionista',
            'logs',
            'anexos',
            'ativo',
            'data_termino',
            'status_titulo',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'observacoes',
            'informacoes_adicionais',
            'tipo_solicitacao'
        )


class SolicitacaoDietaEspecialExportXLSXSerializer(serializers.ModelSerializer):
    codigo_eol_aluno = serializers.SerializerMethodField()
    nome_aluno = serializers.SerializerMethodField()
    nome_escola = serializers.SerializerMethodField()
    classificacao_dieta = serializers.SerializerMethodField()
    protocolo_padrao = serializers.SerializerMethodField()

    def get_codigo_eol_aluno(self, obj):
        return obj.aluno.codigo_eol if obj.aluno else None

    def get_nome_aluno(self, obj):
        return obj.aluno.nome if obj.aluno else None

    def get_nome_escola(self, obj):
        return obj.escola_destino.nome if obj.escola_destino else None

    def get_classificacao_dieta(self, obj):
        return obj.classificacao.nome if obj.classificacao else None

    def get_protocolo_padrao(self, obj):
        return obj.protocolo_padrao.nome_protocolo if obj.protocolo_padrao else None

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'codigo_eol_aluno',
            'nome_aluno',
            'nome_escola',
            'classificacao_dieta',
            'protocolo_padrao'
        )


class PanoramaSerializer(serializers.Serializer):
    periodo = serializers.CharField(
        source='periodo_escolar__nome',
        required=False
    )
    horas_atendimento = serializers.IntegerField(required=False)
    qtde_alunos = serializers.IntegerField(
        source='quantidade_alunos',
        required=False
    )
    qtde_tipo_a = serializers.IntegerField()
    qtde_enteral = serializers.IntegerField()
    qtde_tipo_b = serializers.IntegerField()
    uuid_escola_periodo_escolar = serializers.CharField(
        source='uuid',
        required=False
    )


class SubstituicaoAlimentoProtocoloPadraoSerializer(ModelSerializer):
    alimento = AlimentoSerializer()
    substitutos = ProdutoSimplesSerializer(many=True)
    alimentos_substitutos = AlimentoSerializer(many=True)
    tipo = serializers.CharField(source='get_tipo_display')

    class Meta:
        model = SubstituicaoAlimentoProtocoloPadrao
        fields = '__all__'


class ProtocoloPadraoDietaEspecialSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    substituicoes = serializers.SerializerMethodField()
    historico = serializers.SerializerMethodField()

    class Meta:
        model = ProtocoloPadraoDietaEspecial
        fields = (
            'uuid',
            'nome_protocolo',
            'status',
            'orientacoes_gerais',
            'substituicoes',
            'historico'
        )

    def get_historico(self, obj):
        import json
        return json.loads(obj.historico) if obj.historico else []

    def get_substituicoes(self, obj):
        substituicoes = obj.substituicoes.all().order_by('alimento__nome')
        return SubstituicaoAlimentoProtocoloPadraoSerializer(substituicoes, many=True).data


class ProtocoloPadraoDietaEspecialSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocoloPadraoDietaEspecial
        fields = ('nome_protocolo', 'uuid')


class SolicitacaoDietaEspecialRelatorioTercSerializer(serializers.ModelSerializer):
    cod_eol_aluno = serializers.SerializerMethodField()
    nome_aluno = serializers.SerializerMethodField()
    nome_escola = serializers.SerializerMethodField()
    status_solicitacao = serializers.CharField(
        source='status',
        required=False,
        read_only=True
    )
    rastro_lote = LoteSerializer()
    classificacao = ClassificacaoDietaSerializer()
    protocolo_padrao = ProtocoloPadraoDietaEspecialSimplesSerializer()
    data_ultimo_log = serializers.SerializerMethodField()

    def get_nome_escola(self, obj):
        return obj.rastro_escola.nome if obj.rastro_escola else None

    def get_cod_eol_aluno(self, obj):
        return obj.aluno.codigo_eol if obj.aluno else None

    def get_nome_aluno(self, obj):
        return obj.aluno.nome if obj.aluno else None

    def get_data_ultimo_log(self, obj):
        return datetime.strftime(obj.logs.last().criado_em, '%d/%m/%Y') if (
            obj.logs and obj.status != SolicitacaoDietaEspecial.workflow_class.states.CODAE_AUTORIZADO) else None

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'uuid',
            'id_externo',
            'criado_em',
            'cod_eol_aluno',
            'nome_aluno',
            'nome_escola',
            'status_solicitacao',
            'rastro_lote',
            'classificacao',
            'protocolo_padrao',
            'nome_protocolo',
            'data_ultimo_log'
        )
