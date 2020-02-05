from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from ...dados_comuns.api.serializers import ContatoSerializer, LogSolicitacoesUsuarioSerializer
from ...escola.api.serializers import AlunoSerializer, LoteNomeSerializer, TipoGestaoSerializer
from ...escola.models import Aluno, DiretoriaRegional, Escola
from ..api.serializers_create import AnexoCreateSerializer
from ..models import (
    AlergiaIntolerancia,
    Alimento,
    Anexo,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    SubstituicaoAlimento
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
    class Meta:
        model = Alimento
        fields = '__all__'


class AnexoSerializer(ModelSerializer):
    nome = serializers.CharField()

    class Meta:
        model = Anexo
        fields = ('arquivo', 'nome')


class SubstituicaoAlimentoCreateSerializer(ModelSerializer):
    class Meta:
        model = SubstituicaoAlimento
        fields = '__all__'


class SubstituicaoAlimentoSerializer(ModelSerializer):
    alimento = AlimentoSerializer()
    substitutos = AlimentoSerializer(many=True)

    class Meta:
        model = SubstituicaoAlimento
        fields = '__all__'


class SolicitacaoDietaEspecialCreateSerializer(serializers.ModelSerializer):
    anexos = serializers.ListField(
        child=AnexoCreateSerializer(), required=True
    )
    aluno_json = serializers.JSONField()

    def validate_anexos(self, anexos):
        for anexo in anexos:
            filesize = size(anexo['arquivo'])
            if filesize > DEZ_MB:
                raise serializers.ValidationError('O tamanho máximo de um arquivo é 10MB')
        if not anexos:
            raise serializers.ValidationError('Anexos não pode ser vazio')
        return anexos

    def validate_aluno_json(self, aluno_json):
        for value in ['codigo_eol', 'nome', 'data_nascimento']:
            if value not in aluno_json:
                raise serializers.ValidationError(f'deve ter atributo {value}')
        return aluno_json

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        anexos = validated_data.pop('anexos', [])
        aluno_data = validated_data.pop('aluno_json')
        aluno = self._get_or_create_aluno(aluno_data)
        solicitacao = SolicitacaoDietaEspecial.objects.create(**validated_data)
        solicitacao.aluno = aluno
        solicitacao.save()

        for anexo in anexos:
            data = convert_base64_to_contentfile(anexo.get('arquivo'))
            Anexo.objects.create(
                solicitacao_dieta_especial=solicitacao, arquivo=data, nome=anexo.get('nome', '')
            )

        solicitacao.inicia_fluxo(user=self.context['request'].user)
        return solicitacao

    def _get_or_create_aluno(self, aluno_data):
        escola = self.context['request'].user.vinculo_atual.instituicao
        codigo_eol_aluno = f"{int(aluno_data.get('codigo_eol')):06d}"
        nome_aluno = aluno_data.get('nome')
        data_nascimento_aluno = convert_date_format(
            date=aluno_data.get('data_nascimento'),
            from_format='%d/%m/%Y',
            to_format='%Y-%m-%d'
        )
        deve_ser_no_passado(datetime.datetime.strptime(data_nascimento_aluno, '%Y-%m-%d').date())
        try:
            aluno = Aluno.objects.get(codigo_eol=codigo_eol_aluno)
        except Aluno.DoesNotExist:
            aluno = Aluno(codigo_eol=codigo_eol_aluno,
                          nome=nome_aluno,
                          data_nascimento=data_nascimento_aluno,
                          escola=escola)
            aluno.save()
        return aluno

    class Meta:
        model = SolicitacaoDietaEspecial
        fields = (
            'aluno_json',
            'uuid',
            'nome_completo_pescritor',
            'registro_funcional_pescritor',
            'observacoes',
            'criado_em',
            'anexos'
        )


class SolicitacaoDietaEspecialAutorizarSerializer(SolicitacaoDietaEspecialCreateSerializer):
    def validate(self, data):
        deve_ter_atributos(
            data,
            [
                'alergias_intolerancias',
                'classificacao',
                'registro_funcional_nutricionista',
                'substituicoes'
            ]
        )
        atributos_lista_nao_vazios(data, ['substituicoes', 'alergias_intolerancias'])
        atributos_string_nao_vazios(data, ['registro_funcional_nutricionista'])
        return data

    def update(self, instance, data):
        validated_data = self.validate(data)
        alergias_intolerancias = validated_data.pop('alergias_intolerancias')
        substituicoes = validated_data.pop('substituicoes')

        instance.classificacao_id = validated_data['classificacao']
        instance.registro_funcional_nutricionista = validated_data['registro_funcional_nutricionista']
        instance.informacoes_adicionais = validated_data['informacoes_adicionais']

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
        fields = ['nome']


class EscolaSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSerializer()
    tipo_gestao = TipoGestaoSerializer()
    lote = LoteNomeSerializer()
    contato = ContatoSerializer()

    class Meta:
        model = Escola
        fields = ('nome', 'diretoria_regional', 'tipo_gestao', 'lote', 'contato')


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
            'logs'
        )


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
