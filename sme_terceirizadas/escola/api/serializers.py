from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ...cardapio.models import TipoAlimentacao
from ...dados_comuns.api.serializers import ContatoSerializer, EnderecoSerializer
from ...paineis_consolidados import models
from ...perfil.api.serializers import PerfilSimplesSerializer, SuperAdminTerceirizadaSerializer
from ...perfil.models import Usuario, Vinculo
from ...terceirizada.api.serializers.serializers import ContratoSimplesSerializer, TerceirizadaSimplesSerializer
from ...terceirizada.models import Terceirizada
from ..models import (
    Aluno,
    AlunosMatriculadosPeriodoEscola,
    Codae,
    DiaCalendario,
    DiretoriaRegional,
    Escola,
    EscolaPeriodoEscolar,
    FaixaEtaria,
    FaixaIdadeEscolar,
    LogAlunosMatriculadosPeriodoEscola,
    Lote,
    PeriodoEscolar,
    Subprefeitura,
    TipoGestao,
    TipoUnidadeEscolar
)


class FaixaEtariaSerializer(serializers.ModelSerializer):
    __str__ = serializers.CharField(required=False)

    class Meta:
        model = FaixaEtaria
        exclude = ('id', 'ativo')


class SubsticuicoesTipoAlimentacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoAlimentacao
        exclude = ('id', 'substituicoes',)


class TipoAlimentacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoAlimentacao
        exclude = ('id',)


class PeriodoEscolarSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = PeriodoEscolar
        exclude = ('id',)


class PeriodoEscolarSimplesSerializer(serializers.ModelSerializer):
    # TODO: tirar tipos de alimentacao daqui, tipos de alimentacao são
    # relacionados a TIPOUE + PERIODOESCOLAR

    class Meta:
        model = PeriodoEscolar
        exclude = ('id', 'tipos_alimentacao')


class TipoGestaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoGestao
        exclude = ('id',)


class SubprefeituraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subprefeitura
        exclude = ('id',)


class SubprefeituraSerializerSimples(serializers.ModelSerializer):

    class Meta:
        model = Subprefeitura
        fields = ('codigo_eol', 'nome')


class TipoUnidadeEscolarSerializer(serializers.ModelSerializer):
    periodos_escolares = PeriodoEscolarSimplesSerializer(many=True)

    class Meta:
        model = TipoUnidadeEscolar
        exclude = ('id', 'cardapios')


class LogAlunosMatriculadosPeriodoEscolaSerializer(serializers.ModelSerializer):
    dia = serializers.SerializerMethodField()
    periodo_escolar = PeriodoEscolarSimplesSerializer()

    def get_dia(self, obj):
        return obj.criado_em.strftime('%d')

    class Meta:
        model = LogAlunosMatriculadosPeriodoEscola
        exclude = ('id', 'uuid', 'observacao')


class DiaCalendarioSerializer(serializers.ModelSerializer):
    escola = serializers.CharField(source='escola.nome')
    dia = serializers.SerializerMethodField()

    def get_dia(self, obj):
        return obj.data.strftime('%d')

    class Meta:
        model = DiaCalendario
        exclude = ('id', 'uuid')


class TipoUnidadeEscolarSerializerSimples(serializers.ModelSerializer):

    class Meta:
        model = TipoUnidadeEscolar
        exclude = ('id', 'cardapios', 'periodos_escolares')


class FaixaIdadeEscolarSerializer(serializers.ModelSerializer):

    class Meta:
        model = FaixaIdadeEscolar
        exclude = ('id',)


class DiretoriaRegionalSimplissimaSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiretoriaRegional
        fields = ('uuid', 'nome', 'codigo_eol', 'iniciais')


class DiretoriaRegionalLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiretoriaRegional
        fields = ('uuid', 'iniciais', 'nome', 'codigo_eol')


class LoteReclamacaoSerializer(serializers.ModelSerializer):
    terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = Lote
        fields = ('uuid', 'nome', 'terceirizada')


class EscolaSimplissimaSerializer(serializers.ModelSerializer):
    lote = LoteReclamacaoSerializer()

    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'codigo_eol', 'codigo_codae', 'lote', 'quantidade_alunos')


class DiretoriaRegionalSimplesSerializer(serializers.ModelSerializer):
    escolas = EscolaSimplissimaSerializer(many=True)
    quantidade_alunos = serializers.IntegerField()

    class Meta:
        model = DiretoriaRegional
        exclude = ('id',)


class LoteNomeSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()
    tipo_gestao = serializers.CharField()
    terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = Lote
        fields = ('uuid', 'nome', 'tipo_gestao', 'diretoria_regional', 'terceirizada')  # noqa


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = ('uuid', 'nome')  # noqa


class EscolaNomeCodigoEOLSerializer(serializers.ModelSerializer):
    lote = LoteSerializer()

    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'codigo_eol', 'lote')


class LoteSimplesSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()
    tipo_gestao = TipoGestaoSerializer()
    escolas = EscolaNomeCodigoEOLSerializer(many=True)
    terceirizada = TerceirizadaSimplesSerializer()
    subprefeituras = SubprefeituraSerializer(many=True)

    class Meta:
        model = Lote
        exclude = ('id',)


class EscolaSimplesSerializer(serializers.ModelSerializer):
    lote = LoteNomeSerializer()
    tipo_gestao = TipoGestaoSerializer()
    periodos_escolares = PeriodoEscolarSerializer(many=True)
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()

    class Meta:
        model = Escola
        fields = (
            'uuid',
            'nome',
            'codigo_eol',
            'quantidade_alunos',
            'quantidade_alunos_cei_da_cemei',
            'quantidade_alunos_emei_da_cemei',
            'periodos_escolares',
            'lote',
            'tipo_gestao',
            'diretoria_regional',
            'tipos_contagem'
        )


class EscolaListagemSimplesSelializer(serializers.ModelSerializer):

    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'codigo_eol', 'quantidade_alunos')


class EscolaListagemSimplissimaComDRESelializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()
    lote = serializers.SerializerMethodField()
    tipo_unidade = serializers.SerializerMethodField()

    def get_lote(self, obj):
        return obj.lote.uuid if obj.lote else None

    def get_tipo_unidade(self, obj):
        return obj.tipo_unidade.uuid if obj.tipo_unidade else None

    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'diretoria_regional', 'codigo_eol', 'quantidade_alunos', 'lote', 'tipo_unidade')


class PeriodoEFaixaEtariaCounterSerializer(serializers.BaseSerializer):

    def to_representation(self, dados_entrada):
        """
        Retorna a quantidade de alunos por período e faixa etária.

        Transforma um objeto no seguinte formato:
        {
            'INTEGRAL': {
                '1234-qwer': 42
                '5678-asdf': 51
            },
            'PARCIAL': ...
        }
        em um dicionário no seguinte formato:
        {
            'INTEGRAL': [
                {
                    'faixa_etaria': {'uuid': '1234-qwer', 'inicio': 12, 'fim': 24},
                    'quantidade': 42
                },
                {
                    'faixa_etaria': {'uuid': '5678-asdf', 'inicio': 24, 'fim': 48},
                    'quantidade': 51
                },
            ]
            'PARCIAL': ...
        }
        """
        retorno = {}
        for (periodo, counter) in dados_entrada.items():
            if periodo not in retorno:
                retorno[periodo] = []
            for (uuid_faixa, quantidade) in counter.items():
                faixa_etaria = FaixaEtaria.objects.get(uuid=uuid_faixa)
                retorno[periodo].append({
                    'faixa_etaria': FaixaEtariaSerializer(faixa_etaria).data,
                    'quantidade': quantidade
                })

        return retorno


class EscolaCompletaSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplesSerializer()
    idades = FaixaIdadeEscolarSerializer(many=True)
    tipo_unidade = TipoUnidadeEscolarSerializer()
    tipo_gestao = TipoGestaoSerializer()
    periodos_escolares = PeriodoEscolarSerializer(many=True)
    lote = LoteSimplesSerializer()

    class Meta:
        model = Escola
        exclude = ('id',)


class DiretoriaRegionalCompletaSerializer(serializers.ModelSerializer):
    lotes = LoteSimplesSerializer(many=True)
    escolas = EscolaSimplesSerializer(many=True)

    class Meta:
        model = DiretoriaRegional
        exclude = ('id',)


class TerceirizadaSerializer(serializers.ModelSerializer):
    tipo_alimento_display = serializers.CharField(source='get_tipo_alimento_display')
    tipo_empresa_display = serializers.CharField(source='get_tipo_empresa_display')
    tipo_servico_display = serializers.CharField(source='get_tipo_servico_display')
    nutricionistas = serializers.SerializerMethodField()
    contatos = ContatoSerializer(many=True)
    contratos = ContratoSimplesSerializer(many=True)
    lotes = LoteNomeSerializer(many=True)
    quantidade_alunos = serializers.IntegerField()
    id_externo = serializers.CharField()
    super_admin = SuperAdminTerceirizadaSerializer()

    def get_nutricionistas(self, obj):
        if any(contato.eh_nutricionista for contato in obj.contatos.all()):
            return []
        else:
            content_type = ContentType.objects.get_for_model(Terceirizada)
            return UsuarioNutricionistaSerializer(
                Usuario.objects.filter(
                    vinculos__object_id=obj.id,
                    vinculos__content_type=content_type,
                    crn_numero__isnull=False,
                    super_admin_terceirizadas=False,
                ).filter(
                    Q(vinculos__data_inicial=None, vinculos__data_final=None,
                    vinculos__ativo=False) |
                    Q(vinculos__data_inicial__isnull=False,
                    vinculos__data_final=None, vinculos__ativo=True)
                    # noqa W504 ativo
                ).distinct(),
                many=True
            ).data

    class Meta:
        model = Terceirizada
        exclude = ('id',)


class TipoContagemSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    nome = serializers.CharField()


class VinculoInstituicaoSerializer(serializers.ModelSerializer):
    instituicao = serializers.SerializerMethodField()
    perfil = PerfilSimplesSerializer()

    def get_periodos_escolares(self, obj):
        if isinstance(obj.instituicao, Escola):
            return PeriodoEscolarSerializer(obj.instituicao.periodos_escolares.all(), many=True).data
        else:
            return []

    def get_lotes(self, obj):
        if isinstance(obj.instituicao, (Terceirizada, DiretoriaRegional)):
            return LoteNomeSerializer(obj.instituicao.lotes.all(), many=True).data
        else:
            return []

    def get_diretoria_regional(self, obj):
        if isinstance(obj.instituicao, Escola):
            return DiretoriaRegionalSimplissimaSerializer(obj.instituicao.diretoria_regional).data

    def get_codigo_eol(self, obj):
        if isinstance(obj.instituicao, Escola):
            return obj.instituicao.codigo_eol

    def get_tipo_unidade_escolar(self, obj):
        if isinstance(obj.instituicao, Escola):
            return obj.instituicao.tipo_unidade.uuid

    def get_tipo_unidade_escolar_iniciais(self, obj):
        if isinstance(obj.instituicao, Escola):
            return obj.instituicao.tipo_unidade.iniciais

    def get_tipo_gestao(self, obj):
        if isinstance(obj.instituicao, Escola):
            if not obj.instituicao.tipo_gestao:
                raise ValidationError('Escola não possui tipo de gestão. Favor contatar a CODAE.')
            return obj.instituicao.tipo_gestao.nome

    def get_tipos_contagem(self, obj):
        if isinstance(obj.instituicao, Escola):
            return TipoContagemSerializer(obj.instituicao.tipos_contagem, many=True).data

    def get_endereco(self, obj):
        if isinstance(obj.instituicao, Escola):
            return EnderecoSerializer(obj.instituicao.endereco).data

    def get_contato(self, obj):
        if isinstance(obj.instituicao, Escola):
            return ContatoSerializer(obj.instituicao.contato).data

    def get_instituicao(self, obj):
        instituicao_dict = {'nome': obj.instituicao.nome,
                            'uuid': obj.instituicao.uuid,
                            'codigo_eol': self.get_codigo_eol(obj),
                            'quantidade_alunos': obj.instituicao.quantidade_alunos,
                            'lotes': self.get_lotes(obj),
                            'periodos_escolares': self.get_periodos_escolares(obj),
                            'diretoria_regional': self.get_diretoria_regional(obj),
                            'tipo_unidade_escolar': self.get_tipo_unidade_escolar(obj),
                            'tipo_unidade_escolar_iniciais': self.get_tipo_unidade_escolar_iniciais(obj),
                            'tipo_gestao': self.get_tipo_gestao(obj),
                            'tipos_contagem': self.get_tipos_contagem(obj),
                            'endereco': self.get_endereco(obj),
                            'contato': self.get_contato(obj)}
        if isinstance(obj.instituicao, Escola) and obj.instituicao.eh_cemei:
            instituicao_dict['quantidade_alunos_cei_da_cemei'] = obj.instituicao.quantidade_alunos_cei_da_cemei
            instituicao_dict['quantidade_alunos_emei_da_cemei'] = obj.instituicao.quantidade_alunos_emei_da_cemei
        return instituicao_dict

    class Meta:
        model = Vinculo
        fields = ('uuid', 'instituicao', 'perfil', 'ativo')


class UsuarioNutricionistaSerializer(serializers.ModelSerializer):
    vinculo_atual = VinculoInstituicaoSerializer(required=False)
    contatos = ContatoSerializer(many=True)

    class Meta:
        model = Usuario
        fields = ('nome', 'contatos', 'crn_numero', 'super_admin_terceirizadas', 'vinculo_atual')  # noqa


class UsuarioDetalheSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.CharField()
    vinculo_atual = VinculoInstituicaoSerializer()

    class Meta:
        model = Usuario
        fields = ('uuid', 'cpf', 'nome', 'email', 'tipo_email', 'registro_funcional', 'tipo_usuario', 'date_joined',
                  'vinculo_atual', 'crn_numero', 'cargo')


class CODAESerializer(serializers.ModelSerializer):
    quantidade_alunos = serializers.IntegerField()

    class Meta:
        model = Codae
        fields = '__all__'


class EscolaPeriodoEscolarSerializer(serializers.ModelSerializer):
    quantidade_alunos = serializers.IntegerField()
    escola = EscolaSimplissimaSerializer()
    periodo_escolar = PeriodoEscolarSimplesSerializer()

    class Meta:
        model = EscolaPeriodoEscolar
        fields = ('uuid', 'quantidade_alunos', 'escola', 'periodo_escolar')


class ReponsavelSerializer(serializers.Serializer):
    cpf = serializers.CharField()
    nome = serializers.CharField()


class AlunoSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer(required=False)
    nome_escola = serializers.SerializerMethodField()
    nome_dre = serializers.SerializerMethodField()
    responsaveis = ReponsavelSerializer(many=True)
    possui_dieta_especial = serializers.SerializerMethodField()

    def get_nome_escola(self, obj):
        return f'{obj.escola.nome}' if obj.escola else None

    def get_nome_dre(self, obj):
        return f'{obj.escola.diretoria_regional.nome}' if obj.escola else None

    def get_possui_dieta_especial(self, obj):
        user = self.context['request'].user
        instituicao = user.vinculo_atual.instituicao
        if user.tipo_usuario == 'escola':
            dietas_autorizadas = models.SolicitacoesEscola.get_autorizados_dieta_especial(escola_uuid=instituicao.uuid)
            dietas_inativas = models.SolicitacoesEscola.get_inativas_dieta_especial(escola_uuid=instituicao.uuid)
        elif user.tipo_usuario == 'diretoriaregional':
            dietas_autorizadas = models.SolicitacoesDRE.get_autorizados_dieta_especial(dre_uuid=instituicao.uuid)
            dietas_inativas = models.SolicitacoesDRE.get_inativas_dieta_especial(dre_uuid=instituicao.uuid)
        else:
            dietas_autorizadas = models.SolicitacoesCODAE.get_autorizados_dieta_especial()
            dietas_inativas = models.SolicitacoesCODAE.get_inativas_dieta_especial()

        ids_dietas_autorizadas = dietas_autorizadas.values_list('id', flat=True)
        ids_dietas_inativas = dietas_inativas.values_list('id', flat=True)
        # Juntas as duas querysets.
        dietas_especiais = ids_dietas_autorizadas | ids_dietas_inativas

        return obj.dietas_especiais.filter(id__in=dietas_especiais).exists()

    class Meta:
        model = Aluno
        fields = (
            'uuid',
            'nome',
            'data_nascimento',
            'codigo_eol',
            'escola',
            'nome_escola',
            'nome_dre',
            'responsaveis',
            'cpf',
            'possui_dieta_especial',
            'serie'
        )


class AlunoSimplesSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Escola.objects.all()
    )

    class Meta:
        model = Aluno
        fields = ('uuid', 'nome', 'data_nascimento', 'codigo_eol', 'escola')


class AlunoNaoMatriculadoSerializer(serializers.ModelSerializer):
    responsavel = ReponsavelSerializer()
    codigo_eol_escola = serializers.CharField()
    cpf = serializers.CharField(required=False)

    class Meta:
        model = Aluno
        fields = (
            'uuid',
            'responsavel',
            'codigo_eol_escola',
            'nome',
            'cpf',
            'data_nascimento'
        )


class AlunosMatriculadosPeriodoEscolaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlunosMatriculadosPeriodoEscola
        fields = ('periodo_escolar',)
