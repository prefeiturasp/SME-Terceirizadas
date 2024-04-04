import environ
from rest_framework import serializers
import locale
from ....dados_comuns.validators import deve_ter_extensao_valida
from ....dados_comuns.utils import convert_base64_to_contentfile
from ....dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ....perfil.api.serializers import UsuarioVinculoSerializer
from ....escola.api.serializers import (
    EscolaListagemSimplesSelializer,
    EscolaSimplesSerializer,
    FaixaEtariaSerializer,
    PeriodoEscolarSerializer,
    PeriodoEscolarSimplesSerializer,
    TipoUnidadeEscolarSerializer,
    TipoUnidadeEscolarSerializerSimples,
)
from ....escola.models import FaixaEtaria, Escola
from ....terceirizada.api.serializers.serializers import (
    EditalSerializer,
    TerceirizadaSimplesSerializer,
)
from ....produto.models import TipoAlimento, TipoRecipiente
from ...models import (
    AlteracaoCardapio,
    AlteracaoCardapioCEI,
    AlteracaoCardapioCEMEI,
    Cardapio,
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    FaixaEtariaSubstituicaoAlimentacaoCEI,
    FaixaEtariaSubstituicaoAlimentacaoCEMEICEI,
    GrupoSuspensaoAlimentacao,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar,
    InversaoCardapio,
    MotivoAlteracaoCardapio,
    MotivoDRENaoValida,
    ControleSobras,
    ControleRestos,
    ImagemControleResto,
    MotivoSuspensao,
    QuantidadePorPeriodoSuspensaoAlimentacao,
    SubstituicaoAlimentacaoNoPeriodoEscolar,
    SubstituicaoAlimentacaoNoPeriodoEscolarCEI,
    SubstituicaoAlimentacaoNoPeriodoEscolarCEMEICEI,
    SubstituicaoAlimentacaoNoPeriodoEscolarCEMEIEMEI,
    SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    SuspensaoAlimentacao,
    SuspensaoAlimentacaoDaCEI,
    SuspensaoAlimentacaoNoPeriodoEscolar,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar,
)
from .serializers_create import (
    DatasIntervaloAlteracaoCardapioCEMEICreateSerializer,
    DatasIntervaloAlteracaoCardapioSerializerCreateSerializer,
)


class TipoAlimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlimentacao
        exclude = ("id",)


class TipoAlimentacaoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlimentacao
        fields = (
            "uuid",
            "nome",
        )


class SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer(
    serializers.ModelSerializer
):
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True)
    combo = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        queryset=ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all(),
    )

    class Meta:
        model = SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = (
            "uuid",
            "tipos_alimentacao",
            "combo",
            "label",
        )


class CombosVinculoTipoAlimentoSimplesSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True)
    substituicoes = SubstituicaoDoComboVinculoTipoAlimentoSimplesSerializer(many=True)
    vinculo = serializers.SlugRelatedField(
        slug_field="uuid",
        required=True,
        queryset=VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.all(),
    )
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        label = ""
        for tipo_alimentacao in obj.tipos_alimentacao.all():
            if len(label) == 0:
                label += tipo_alimentacao.nome
            else:
                label += f" e {tipo_alimentacao.nome}"
        return label

    class Meta:
        model = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = (
            "uuid",
            "tipos_alimentacao",
            "vinculo",
            "substituicoes",
            "label",
        )


class CombosVinculoTipoAlimentoSimplissimaSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        label = ""
        for tipo_alimentacao in obj.tipos_alimentacao.all():
            if len(label) == 0:
                label += tipo_alimentacao.nome
            else:
                label += f" e {tipo_alimentacao.nome}"
        return label

    class Meta:
        model = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
        fields = (
            "uuid",
            "label",
        )


class HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolarSerializer(
    serializers.ModelSerializer
):
    escola = EscolaListagemSimplesSelializer()
    tipo_alimentacao = TipoAlimentacaoSerializer()
    periodo_escolar = PeriodoEscolarSimplesSerializer()

    class Meta:
        model = HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar
        fields = (
            "uuid",
            "hora_inicial",
            "hora_final",
            "escola",
            "tipo_alimentacao",
            "periodo_escolar",
        )


class VinculoTipoAlimentoSimplesSerializer(serializers.ModelSerializer):
    tipo_unidade_escolar = TipoUnidadeEscolarSerializerSimples()
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True, read_only=True)

    class Meta:
        model = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
        fields = (
            "uuid",
            "tipo_unidade_escolar",
            "periodo_escolar",
            "tipos_alimentacao",
        )


class VinculoTipoAlimentoPeriodoSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True, read_only=True)

    def get_nome(self, obj):
        return obj.periodo_escolar.nome

    class Meta:
        model = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
        fields = (
            "nome",
            "tipos_alimentacao",
        )


class CardapioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cardapio
        exclude = ("id",)


class CardapioSerializer(serializers.ModelSerializer):
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True, read_only=True)
    tipos_unidade_escolar = TipoUnidadeEscolarSerializer(many=True, read_only=True)
    edital = EditalSerializer()

    class Meta:
        model = Cardapio
        exclude = ("id",)


class InversaoCardapioSerializer(serializers.ModelSerializer):
    cardapio_de = CardapioSimplesSerializer()
    cardapio_para = CardapioSimplesSerializer()
    escola = EscolaSimplesSerializer()
    id_externo = serializers.CharField()
    prioridade = serializers.CharField()
    data = (
        serializers.DateField()
    )  # representa data do objeto, a menor entre data_de e data_para
    data_de = serializers.DateField()
    data_para = serializers.DateField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSimplesSerializer(many=True)

    class Meta:
        model = InversaoCardapio
        exclude = ("id", "criado_por")


class InversaoCardapioSimpleserializer(serializers.ModelSerializer):
    id_externo = serializers.CharField()
    prioridade = serializers.CharField()
    escola = EscolaSimplesSerializer()
    data = serializers.DateField()

    class Meta:
        model = InversaoCardapio
        exclude = (
            "id",
            "criado_por",
            "cardapio_de",
            "cardapio_para",
        )


class MotivoSuspensaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoSuspensao
        exclude = ("id",)


class SuspensaoAlimentacaoDaCEISerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    motivo = MotivoSuspensaoSerializer()
    periodos_escolares = PeriodoEscolarSimplesSerializer(many=True)
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = SuspensaoAlimentacaoDaCEI
        exclude = ("id",)


class SuspensaoAlimentacaoNoPeriodoEscolarSerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = SuspensaoAlimentacaoNoPeriodoEscolar
        exclude = ("id", "suspensao_alimentacao")


class SuspensaoAlimentacaoSerializer(serializers.ModelSerializer):
    motivo = MotivoSuspensaoSerializer()

    class Meta:
        model = SuspensaoAlimentacao
        exclude = ("id", "grupo_suspensao")


class QuantidadePorPeriodoSuspensaoAlimentacaoSerializer(serializers.ModelSerializer):
    periodo_escolar = PeriodoEscolarSimplesSerializer()
    tipos_alimentacao = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = QuantidadePorPeriodoSuspensaoAlimentacao
        exclude = ("id", "grupo_suspensao")


class GrupoSuspensaoAlimentacaoSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    quantidades_por_periodo = QuantidadePorPeriodoSuspensaoAlimentacaoSerializer(
        many=True
    )
    suspensoes_alimentacao = SuspensaoAlimentacaoSerializer(many=True)
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = GrupoSuspensaoAlimentacao
        exclude = ("id",)


class GrupoSuspensaoAlimentacaoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoSuspensaoAlimentacao
        exclude = ("id", "criado_por", "escola")


class GrupoSupensaoAlimentacaoListagemSimplesSerializer(serializers.ModelSerializer):
    escola = EscolaListagemSimplesSelializer()
    prioridade = serializers.CharField()

    class Meta:
        model = GrupoSuspensaoAlimentacao
        fields = (
            "uuid",
            "id_externo",
            "status",
            "prioridade",
            "criado_em",
            "escola",
        )


class MotivoAlteracaoCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoAlteracaoCardapio
        exclude = ("id",)


class FaixaEtariaSubstituicaoAlimentacaoCEISerializer(serializers.ModelSerializer):
    faixa_etaria = FaixaEtariaSerializer()

    class Meta:
        model = FaixaEtariaSubstituicaoAlimentacaoCEI
        exclude = ("id",)


class SubstituicoesAlimentacaoNoPeriodoEscolarSerializerBase(
    serializers.ModelSerializer
):
    periodo_escolar = PeriodoEscolarSerializer()
    alteracao_cardapio = serializers.SlugRelatedField(
        slug_field="uuid", required=False, queryset=AlteracaoCardapio.objects.all()
    )
    tipos_alimentacao_de = TipoAlimentacaoSerializer(many=True)


class SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(
    SubstituicoesAlimentacaoNoPeriodoEscolarSerializerBase
):
    tipos_alimentacao_para = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolar
        exclude = ("id",)


class SubstituicoesAlimentacaoNoPeriodoEscolarCEISerializer(
    SubstituicoesAlimentacaoNoPeriodoEscolarSerializerBase
):
    tipo_alimentacao_para = TipoAlimentacaoSerializer()

    faixas_etarias = FaixaEtariaSubstituicaoAlimentacaoCEISerializer(many=True)

    def to_representation(self, instance):
        retorno = super().to_representation(instance)

        faixas_etarias_da_solicitacao = FaixaEtaria.objects.filter(
            uuid__in=[f.faixa_etaria.uuid for f in instance.faixas_etarias.all()]
        )

        # Inclui o total de alunos nas faixas etárias num período
        qtde_alunos = (
            instance.alteracao_cardapio.escola.alunos_por_periodo_e_faixa_etaria(
                instance.alteracao_cardapio.data, faixas_etarias_da_solicitacao
            )
        )

        nome_periodo_correcoes = {
            "PARCIAL": "INTEGRAL",
            "MANHA": "MANHÃ",
        }
        nome_periodo = nome_periodo_correcoes.get(
            instance.periodo_escolar.nome, instance.periodo_escolar.nome
        )

        for faixa_etaria in retorno["faixas_etarias"]:
            try:
                uuid_faixa_etaria = faixa_etaria["faixa_etaria"]["uuid"]
                faixa_etaria["total_alunos_no_periodo"] = qtde_alunos[nome_periodo][
                    uuid_faixa_etaria
                ]
            except KeyError:
                continue

        return retorno

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolarCEI
        exclude = ("id",)


class AlteracaoCardapioSerializerBase(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    motivo = MotivoAlteracaoCardapioSerializer()
    foi_solicitado_fora_do_prazo = serializers.BooleanField()
    eh_alteracao_com_lanche_repetida = serializers.BooleanField()
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    prioridade = serializers.CharField()


class AlteracaoCardapioSerializer(AlteracaoCardapioSerializerBase):
    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarSerializer(many=True)
    datas_intervalo = DatasIntervaloAlteracaoCardapioSerializerCreateSerializer(
        many=True
    )
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = AlteracaoCardapio
        exclude = ("id",)


class AlteracaoCardapioCEISerializer(AlteracaoCardapioSerializerBase):
    substituicoes = SubstituicoesAlimentacaoNoPeriodoEscolarCEISerializer(many=True)
    rastro_terceirizada = TerceirizadaSimplesSerializer()

    class Meta:
        model = AlteracaoCardapioCEI
        exclude = ("id",)


class FaixaEtariaSubstituicaoAlimentacaoCEMEICEISerializer(serializers.ModelSerializer):
    faixa_etaria = FaixaEtariaSerializer()

    class Meta:
        model = FaixaEtariaSubstituicaoAlimentacaoCEMEICEI
        exclude = ("id",)


class SubstituicaoAlimentacaoNoPeriodoEscolarCEMEICEISerializer(
    serializers.ModelSerializer
):
    periodo_escolar = PeriodoEscolarSerializer()
    faixas_etarias = FaixaEtariaSubstituicaoAlimentacaoCEMEICEISerializer(many=True)
    tipos_alimentacao_de = TipoAlimentacaoSerializer(many=True)
    tipos_alimentacao_para = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolarCEMEICEI
        exclude = ("id",)


class SubstituicaoAlimentacaoNoPeriodoEscolarCEMEIEMEISerializer(
    serializers.ModelSerializer
):
    periodo_escolar = PeriodoEscolarSerializer()
    tipos_alimentacao_de = TipoAlimentacaoSerializer(many=True)
    tipos_alimentacao_para = TipoAlimentacaoSerializer(many=True)

    class Meta:
        model = SubstituicaoAlimentacaoNoPeriodoEscolarCEMEIEMEI
        exclude = ("id",)


class AlteracaoCardapioCEMEISerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    motivo = MotivoAlteracaoCardapioSerializer()
    foi_solicitado_fora_do_prazo = serializers.BooleanField()
    id_externo = serializers.CharField()
    logs = LogSolicitacoesUsuarioSerializer(many=True)
    prioridade = serializers.CharField()
    substituicoes_cemei_cei_periodo_escolar = (
        SubstituicaoAlimentacaoNoPeriodoEscolarCEMEICEISerializer(many=True)
    )
    substituicoes_cemei_emei_periodo_escolar = (
        SubstituicaoAlimentacaoNoPeriodoEscolarCEMEIEMEISerializer(many=True)
    )
    datas_intervalo = DatasIntervaloAlteracaoCardapioCEMEICreateSerializer(many=True)

    class Meta:
        model = AlteracaoCardapioCEMEI
        exclude = ("id",)


class AlteracaoCardapioSimplesSerializer(serializers.ModelSerializer):
    prioridade = serializers.CharField()

    class Meta:
        model = AlteracaoCardapio
        exclude = ("id", "criado_por", "escola", "motivo")


class MotivoDRENaoValidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoDRENaoValida
        exclude = ('id',)


class ControleSobrasSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    usuario = UsuarioVinculoSerializer()
    tipo_alimentacao_nome = serializers.SerializerMethodField()
    tipo_alimento_nome = serializers.SerializerMethodField()
    tipo_recipiente_nome = serializers.SerializerMethodField()

    def get_tipo_alimentacao_nome(self, obj):
        return obj.tipo_alimentacao.nome

    def get_tipo_alimento_nome(self, obj):
        return obj.tipo_alimento.nome

    def get_tipo_recipiente_nome(self, obj):
        return obj.tipo_recipiente.nome

    class Meta:
        model = ControleSobras
        exclude = ('id',)


class ControleSobrasCreateSerializer(serializers.Serializer):
    escola = serializers.CharField(required=True)
    tipo_alimentacao = serializers.CharField(required=True)
    tipo_alimento = serializers.CharField(required=True)
    peso_alimento = serializers.CharField(required=True)
    tipo_recipiente = serializers.CharField(required=True)
    peso_recipiente = serializers.CharField(required=True)
    peso_sobra = serializers.CharField(required=True)
    data_hora_medicao = serializers.DateTimeField(required=True)

    def create(self, validated_data):
        escola = Escola.objects.get(uuid=validated_data['escola'])
        tipo_alimentacao = TipoAlimentacao.objects.get(uuid=validated_data['tipo_alimentacao'])
        tipo_alimento = TipoAlimento.objects.get(uuid=validated_data['tipo_alimento'])
        peso_alimento = validated_data['peso_alimento']
        tipo_recipiente = TipoRecipiente.objects.get(uuid=validated_data['tipo_recipiente'])
        peso_recipiente = validated_data['peso_recipiente']
        peso_sobra = validated_data['peso_sobra']
        usuario = self.context['request'].user
        data_hora_medicao = validated_data['data_hora_medicao']

        try:
            item = ControleSobras.objects.create(
                escola=escola,
                tipo_alimentacao=tipo_alimentacao,
                tipo_alimento=tipo_alimento,
                peso_alimento=peso_alimento,
                tipo_recipiente=tipo_recipiente,
                peso_recipiente=peso_recipiente,
                peso_sobra=peso_sobra,
                usuario=usuario,
                data_hora_medicao=data_hora_medicao
            )
            return item
        except Exception as e:
            print(e)
            raise serializers.ValidationError('Erro ao criar ControleSobras.')


class ImagemControleRestoCreateSerializer(serializers.ModelSerializer):
    arquivo = serializers.CharField()
    nome = serializers.CharField()

    def validate_nome(self, nome):
        deve_ter_extensao_valida(nome)
        return nome

    class Meta:
        model = ImagemControleResto
        fields = ('arquivo', 'nome')


class ImagemControleRestoSerializer(serializers.ModelSerializer):
    arquivo = serializers.SerializerMethodField()

    def get_arquivo(self, obj):
        env = environ.Env()
        api_url = env.str('URL_ANEXO', default='http://localhost:8000')
        return f'{api_url}{obj.arquivo.url}'

    class Meta:
        model = ImagemControleResto
        fields = ('arquivo', 'nome')


class ControleRestosSerializer(serializers.ModelSerializer):
    escola = EscolaSimplesSerializer()
    usuario = UsuarioVinculoSerializer()
    tipo_alimentacao_nome = serializers.SerializerMethodField()
    imagens = serializers.ListField(
        child=ImagemControleRestoSerializer(), required=True
    )

    def get_tipo_alimentacao_nome(self, obj):
        return obj.tipo_alimentacao.nome

    class Meta:
        model = ControleRestos
        exclude = ('id',)


class ControleRestosCreateSerializer(serializers.Serializer):
    escola = serializers.CharField(required=True)
    tipo_alimentacao = serializers.CharField(required=True)
    peso_resto = serializers.CharField(required=True)
    cardapio = serializers.CharField(required=True)
    resto_predominante = serializers.CharField(required=True)
    quantidade_distribuida = serializers.CharField(required=True)
    data_hora_medicao = serializers.DateTimeField(required=True)
    imagens = serializers.ListField(
        child=ImagemControleRestoCreateSerializer(), required=True
    )

    def create(self, validated_data):
        escola = Escola.objects.get(uuid=validated_data['escola'])
        tipo_alimentacao = TipoAlimentacao.objects.get(uuid=validated_data['tipo_alimentacao'])
        peso_resto = validated_data['peso_resto']
        cardapio = validated_data['cardapio']
        resto_predominante = validated_data['resto_predominante']
        usuario = self.context['request'].user
        imagens = validated_data.pop('imagens', [])
        quantidade_distribuida = validated_data['quantidade_distribuida']
        data_hora_medicao = validated_data['data_hora_medicao']

        try:
            item = ControleRestos.objects.create(
                escola=escola,
                tipo_alimentacao=tipo_alimentacao,
                peso_resto=peso_resto,
                cardapio=cardapio,
                resto_predominante=resto_predominante,
                usuario=usuario,
                data_hora_medicao=data_hora_medicao,
                quantidade_distribuida=quantidade_distribuida
            )

            for imagem in imagens:
                data = convert_base64_to_contentfile(imagem.get('arquivo'))
                ImagemControleResto.objects.create(
                    controle_resto=item,
                    arquivo=data,
                    nome=imagem.get('nome', '')
                )

            return item
        except Exception as e:
            print(e)
            raise serializers.ValidationError('Erro ao criar ControleRestos.')


def serialize_relatorio_controle_restos(row):
    data_medicao, dre_nome, escola_nome, quantidade_distribuida_soma, peso_resto_soma, num_refeicoes, resto_per_capita, percent_resto = row

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    def format_float(value, format=True):
        if (value is None):
            return None

        return locale.format_string('%.2f', float(value), grouping=True)

    def format_int(value):
        if (value is None):
            return None

        return int(value)

    return {
        'dre_nome': dre_nome,
        'escola_nome': escola_nome,
        'data_medicao': data_medicao.strftime('%d/%m/%Y') if data_medicao else None,
        'quantidade_distribuida_soma': format_float(quantidade_distribuida_soma),
        'peso_resto_soma': format_float(peso_resto_soma),
        'num_refeicoes': format_int(num_refeicoes),
        'resto_per_capita': format_float(resto_per_capita),
        'percent_resto': format_float(percent_resto),
    }


def serialize_relatorio_controle_sobras(row):

    data_medicao, dre_nome, escola_nome, tipo_alimentacao_nome, tipo_alimento_nome, quantidade_distribuida, peso_sobra, frequencia, total_primeira_oferta, total_repeticao, percentual_sobra, media_por_aluno, media_por_refeicao = row

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    def format_float(value, format=True):
        if (value is None):
            return None

        return locale.format_string('%.2f', float(value), grouping=True)

    def format_int(value):
        if (value is None):
            return None

        return int(value)

    return {
        'dre_nome': dre_nome,
        'escola_nome': escola_nome,
        'tipo_alimentacao_nome': tipo_alimentacao_nome,
        'tipo_alimento_nome': tipo_alimento_nome,
        'data_medicao': data_medicao.strftime('%d/%m/%Y') if data_medicao else None,
        'quantidade_distribuida': format_float(quantidade_distribuida),
        'peso_sobra': format_float(peso_sobra),
        'frequencia': format_int(frequencia),
        'total_primeira_oferta': format_int(total_primeira_oferta),
        'total_repeticao': format_int(total_repeticao),
        'percentual_sobra': format_float(percentual_sobra),
        'media_por_aluno': format_float(media_por_aluno),
        'media_por_refeicao': format_float(media_por_refeicao),
    }
