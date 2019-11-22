from rest_framework import serializers

from ...cardapio.models import TipoAlimentacao
from ...dados_comuns.api.serializers import ContatoSerializer
from ...perfil.api.serializers import PerfilSimplesSerializer
from ...perfil.models import Usuario, Vinculo
from ...terceirizada.api.serializers.serializers import (
    ContratoSimplesSerializer,
    NutricionistaSerializer,
    TerceirizadaSimplesSerializer
)
from ...terceirizada.models import Terceirizada
from ..models import (
    Codae,
    DiretoriaRegional,
    Escola,
    FaixaIdadeEscolar,
    Lote,
    PeriodoEscolar,
    Subprefeitura,
    TipoGestao,
    TipoUnidadeEscolar
)


class SubsticuicoesTipoAlimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlimentacao
        exclude = ('id', 'substituicoes',)


class TipoAlimentacaoSerializer(serializers.ModelSerializer):
    substituicoes = SubsticuicoesTipoAlimentacaoSerializer(many=True)

    class Meta:
        model = TipoAlimentacao
        exclude = ('id',)


class PeriodoEscolarSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = PeriodoEscolar
        exclude = ('id',)


class PeriodoEscolarSimplesSerializer(serializers.ModelSerializer):
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


class TipoUnidadeEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUnidadeEscolar
        exclude = ('id', 'cardapios')


class FaixaIdadeEscolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaixaIdadeEscolar
        exclude = ('id',)


class DiretoriaRegionalSimplissimaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiretoriaRegional
        fields = ('uuid', 'nome')


class EscolaSimplissimaSerializer(serializers.ModelSerializer):
    lote = serializers.SerializerMethodField()

    def get_lote(self, obj):
        return f'{obj.lote.nome} - {obj.lote.iniciais}' if obj.lote else None

    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'codigo_eol', 'lote', 'quantidade_alunos')


class DiretoriaRegionalSimplesSerializer(serializers.ModelSerializer):
    escolas = EscolaSimplissimaSerializer(many=True)
    quantidade_alunos = serializers.IntegerField()

    class Meta:
        model = DiretoriaRegional
        exclude = ('id',)


class LoteSimplesSerializer(serializers.ModelSerializer):
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()
    tipo_gestao = TipoGestaoSerializer()
    escolas = EscolaSimplissimaSerializer(many=True)
    terceirizada = TerceirizadaSimplesSerializer()
    subprefeituras = SubprefeituraSerializer(many=True)

    class Meta:
        model = Lote
        exclude = ('id',)


class LoteNomeSerializer(serializers.ModelSerializer):
    tipo_gestao = serializers.CharField()

    class Meta:
        model = Lote
        fields = ('uuid', 'nome', 'tipo_gestao')


class EscolaSimplesSerializer(serializers.ModelSerializer):
    lote = LoteNomeSerializer()
    tipo_gestao = TipoGestaoSerializer()
    periodos_escolares = PeriodoEscolarSerializer(many=True)
    diretoria_regional = DiretoriaRegionalSimplissimaSerializer()

    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'codigo_eol', 'quantidade_alunos', 'periodos_escolares', 'lote', 'tipo_gestao',
                  'diretoria_regional')


class EscolaListagemSimplesSelializer(serializers.ModelSerializer):
    class Meta:
        model = Escola
        fields = ('uuid', 'nome', 'codigo_eol', 'quantidade_alunos')


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
    nutricionistas = NutricionistaSerializer(many=True)
    contatos = ContatoSerializer(many=True)
    contratos = ContratoSimplesSerializer(many=True)
    lotes = LoteNomeSerializer(many=True)
    quantidade_alunos = serializers.IntegerField()
    id_externo = serializers.CharField()

    class Meta:
        model = Terceirizada
        exclude = ('id',)


class VinculoInstituicaoSerializer(serializers.ModelSerializer):
    instituicao = serializers.SerializerMethodField()
    perfil = PerfilSimplesSerializer()

    def get_periodos_escolares(self, obj):
        if isinstance(obj.instituicao, Escola):
            return PeriodoEscolarSerializer(obj.instituicao.periodos_escolares.all(), many=True).data
        else:
            return []

    def get_lotes(self, obj):
        if isinstance(obj.instituicao, Terceirizada):
            return LoteNomeSerializer(obj.instituicao.lotes.all(), many=True).data
        else:
            return []

    def get_escolas(self, obj):
        if isinstance(obj.instituicao, DiretoriaRegional):
            return EscolaListagemSimplesSelializer(obj.instituicao.escolas.all(), many=True).data
        else:
            return []

    def get_instituicao(self, obj):
        return {'nome': obj.instituicao.nome,
                'uuid': obj.instituicao.uuid,
                'quantidade_alunos': obj.instituicao.quantidade_alunos,
                'lotes': self.get_lotes(obj),
                'periodos_escolares': self.get_periodos_escolares(obj),
                'escolas': self.get_escolas(obj)}

    class Meta:
        model = Vinculo
        fields = ('instituicao', 'perfil')


class UsuarioDetalheSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.CharField()
    vinculo_atual = VinculoInstituicaoSerializer()

    class Meta:
        model = Usuario
        fields = ('uuid', 'cpf', 'nome', 'email', 'registro_funcional', 'tipo_usuario', 'date_joined', 'vinculo_atual')


class CODAESerializer(serializers.ModelSerializer):
    quantidade_alunos = serializers.IntegerField()

    class Meta:
        model = Codae
        fields = '__all__'
