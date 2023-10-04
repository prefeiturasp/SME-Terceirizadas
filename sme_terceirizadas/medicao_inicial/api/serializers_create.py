import calendar
import json
from datetime import datetime

import environ
from rest_framework import serializers

from sme_terceirizadas.cardapio.models import TipoAlimentacao
from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile, update_instance_from_dict
from sme_terceirizadas.dados_comuns.validators import deve_ter_extensao_xls_xlsx_pdf
from sme_terceirizadas.escola.api.serializers_create import AlunoPeriodoParcialCreateSerializer
from sme_terceirizadas.escola.models import (
    Aluno,
    AlunoPeriodoParcial,
    Escola,
    FaixaEtaria,
    LogAlunosMatriculadosPeriodoEscola,
    PeriodoEscolar,
    TipoUnidadeEscolar
)
from sme_terceirizadas.medicao_inicial.models import (
    CategoriaMedicao,
    DiaSobremesaDoce,
    GrupoMedicao,
    Medicao,
    OcorrenciaMedicaoInicial,
    Responsavel,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)
from sme_terceirizadas.perfil.models import Usuario

from ..utils import log_alteracoes_escola_corrige_periodo
from ..validators import (
    validate_lancamento_alimentacoes_medicao,
    validate_lancamento_dietas,
    validate_lancamento_inclusoes
)


class DiaSobremesaDoceCreateSerializer(serializers.ModelSerializer):
    tipo_unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all(),
        required=True,
    )

    criado_por = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Usuario.objects.all(),
        required=True
    )

    class Meta:
        model = DiaSobremesaDoce
        exclude = ('id',)


class DiaSobremesaDoceCreateManySerializer(serializers.ModelSerializer):
    tipo_unidades = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=TipoUnidadeEscolar.objects.all(),
        many=True,
        required=True,
    )

    def create(self, validated_data):
        """Cria ou atualiza dias de sobremesa doce."""
        dia_sobremesa_doce = None
        DiaSobremesaDoce.objects.filter(data=validated_data['data']).exclude(
            tipo_unidade__in=validated_data['tipo_unidades']).delete()
        dias_sobremesa_doce = DiaSobremesaDoce.objects.filter(data=validated_data['data'])
        for tipo_unidade in validated_data['tipo_unidades']:
            if not dias_sobremesa_doce.filter(tipo_unidade=tipo_unidade).exists():
                dia_sobremesa_doce = DiaSobremesaDoce(
                    criado_por=self.context['request'].user,
                    data=validated_data['data'],
                    tipo_unidade=tipo_unidade
                )
                dia_sobremesa_doce.save()
        return dia_sobremesa_doce

    class Meta:
        model = DiaSobremesaDoce
        fields = ('tipo_unidades', 'data', 'uuid')


class OcorrenciaMedicaoInicialCreateSerializer(serializers.ModelSerializer):
    ultimo_arquivo = serializers.SerializerMethodField()
    nome_ultimo_arquivo = serializers.CharField()

    def get_ultimo_arquivo(self, obj):
        env = environ.Env()
        api_url = env.str('URL_ANEXO', default='http://localhost:8000')
        return f'{api_url}{obj.ultimo_arquivo.url}'

    def validate_nome_ultimo_arquivo(self, nome_ultimo_arquivo):
        deve_ter_extensao_xls_xlsx_pdf(nome_ultimo_arquivo)
        return nome_ultimo_arquivo

    class Meta:
        model = OcorrenciaMedicaoInicial
        exclude = ('id', 'solicitacao_medicao_inicial',)


class ResponsavelCreateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField()
    rf = serializers.CharField()

    class Meta:
        model = Responsavel
        exclude = ('id', 'solicitacao_medicao_inicial',)


class SolicitacaoMedicaoInicialCreateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    tipo_contagem_alimentacoes = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TipoContagemAlimentacao.objects.all(),
    )
    alunos_periodo_parcial = AlunoPeriodoParcialCreateSerializer(many=True, required=False)
    responsaveis = ResponsavelCreateSerializer(many=True)
    com_ocorrencias = serializers.BooleanField(required=False)
    ocorrencia = OcorrenciaMedicaoInicialCreateSerializer(required=False)
    logs = LogSolicitacoesUsuarioSerializer(many=True, required=False)

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        responsaveis_dict = validated_data.pop('responsaveis', [])
        alunos_uuids = validated_data.pop('alunos_periodo_parcial', [])

        solicitacao = SolicitacaoMedicaoInicial.objects.create(**validated_data)

        for responsavel in responsaveis_dict:
            Responsavel.objects.create(
                solicitacao_medicao_inicial=solicitacao,
                nome=responsavel.get('nome', ''),
                rf=responsavel.get('rf', '')
            )
        if alunos_uuids:
            escola_associada = validated_data.get('escola')
            for aluno in alunos_uuids:
                AlunoPeriodoParcial.objects.create(
                    solicitacao_medicao_inicial=solicitacao,
                    aluno=Aluno.objects.get(uuid=aluno.get('aluno', '')),
                    escola=escola_associada
                )

        solicitacao.inicia_fluxo(user=self.context['request'].user)
        return solicitacao

    def valida_finalizar_medicao_emef_emei(self, instance):
        iniciais_emef_emei = ['EMEI', 'EMEF', 'EMEFM', 'CEU EMEF', 'CEU EMEI', 'CIEJA']
        iniciais_escola = instance.escola.tipo_unidade.iniciais
        if iniciais_escola not in iniciais_emef_emei:
            return

        lista_erros = []

        if instance.status == SolicitacaoMedicaoInicial.workflow_class.MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE:
            lista_erros = validate_lancamento_alimentacoes_medicao(instance, lista_erros)
            lista_erros = validate_lancamento_inclusoes(instance, lista_erros)
            lista_erros = validate_lancamento_dietas(instance, lista_erros)

        if lista_erros:
            raise serializers.ValidationError(lista_erros)

    def cria_valores_medicao_logs_alunos_matriculados(self, instance: SolicitacaoMedicaoInicial):
        escola = instance.escola
        valores_medicao_a_criar = []
        logs_do_mes = LogAlunosMatriculadosPeriodoEscola.objects.filter(
            criado_em__month=instance.mes,
            criado_em__year=instance.ano,
            escola=escola
        )
        categoria = CategoriaMedicao.objects.get(nome='ALIMENTAÇÃO')
        quantidade_dias_mes = calendar.monthrange(int(instance.ano), int(instance.mes))[1]
        for dia in range(1, quantidade_dias_mes + 1):
            for periodo_escolar in escola.periodos_escolares_com_alunos:
                try:
                    medicao = instance.medicoes.get(periodo_escolar__nome=periodo_escolar)
                except Medicao.DoesNotExist:
                    medicao = Medicao.objects.create(
                        solicitacao_medicao_inicial=instance,
                        periodo_escolar=PeriodoEscolar.objects.get(nome=periodo_escolar)
                    )
                if not medicao.valores_medicao.filter(
                    categoria_medicao=categoria,
                    dia=f'{dia:02d}',
                    nome_campo='matriculados',
                ).exists():
                    log = logs_do_mes.filter(
                        periodo_escolar__nome=periodo_escolar,
                        criado_em__day=dia
                    ).first()
                    valor_medicao = ValorMedicao(
                        medicao=medicao,
                        categoria_medicao=categoria,
                        dia=f'{dia:02d}',
                        nome_campo='matriculados',
                        valor=log.quantidade_alunos if log else 0
                    )
                    valores_medicao_a_criar.append(valor_medicao)

        ValorMedicao.objects.bulk_create(valores_medicao_a_criar)

    def cria_valores_medicao_logs(self, instance):
        self.cria_valores_medicao_logs_alunos_matriculados(instance)

    def update(self, instance, validated_data):  # noqa C901
        responsaveis_dict = self.context['request'].data.get('responsaveis', None)
        key_com_ocorrencias = validated_data.get('com_ocorrencias', None)
        alunos_uuids_dict = self.context['request'].data.get('alunos_periodo_parcial', None)

        validated_data.pop('alunos_periodo_parcial', None)
        validated_data.pop('responsaveis', None)
        update_instance_from_dict(instance, validated_data, save=True)

        if responsaveis_dict:
            responsaveis = json.loads(responsaveis_dict)
            instance.responsaveis.all().delete()
            for responsavel in responsaveis:
                Responsavel.objects.create(
                    solicitacao_medicao_inicial=instance,
                    nome=responsavel.get('nome', ''),
                    rf=responsavel.get('rf', '')
                )

        if alunos_uuids_dict:
            alunos_uuids = json.loads(alunos_uuids_dict)
            escola_associada = validated_data.get('escola')
            instance.alunos_periodo_parcial.all().delete()
            for aluno_uuid in alunos_uuids:
                AlunoPeriodoParcial.objects.create(
                    solicitacao_medicao_inicial=instance,
                    aluno=Aluno.objects.get(uuid=aluno_uuid),
                    escola=escola_associada
                )

        anexos_string = self.context['request'].data.get('anexos', None)
        if anexos_string:
            anexos = json.loads(anexos_string)
            for anexo in anexos:
                if '.pdf' in anexo['nome']:
                    arquivo = convert_base64_to_contentfile(anexo['base64'])
                    OcorrenciaMedicaoInicial.objects.create(
                        solicitacao_medicao_inicial=instance,
                        ultimo_arquivo=arquivo,
                        nome_ultimo_arquivo=anexo.get('nome')
                    )
        if key_com_ocorrencias is not None and self.context['request'].data.get('finaliza_medicao') == 'true':
            self.cria_valores_medicao_logs(instance)
            self.valida_finalizar_medicao_emef_emei(instance)
            instance.ue_envia(user=self.context['request'].user)
            if hasattr(instance, 'ocorrencia'):
                instance.ocorrencia.ue_envia(user=self.context['request'].user, anexos=anexos)
            for medicao in instance.medicoes.all():
                medicao.ue_envia(user=self.context['request'].user)

        return instance

    class Meta:
        model = SolicitacaoMedicaoInicial
        exclude = ('id', 'criado_por',)


class ValorMedicaoCreateUpdateSerializer(serializers.ModelSerializer):
    valor = serializers.CharField()
    nome_campo = serializers.CharField()
    categoria_medicao = serializers.SlugRelatedField(
        slug_field='id',
        required=True,
        queryset=CategoriaMedicao.objects.all(),
    )
    tipo_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        allow_null=True,
        queryset=TipoAlimentacao.objects.all()
    )
    faixa_etaria = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        allow_null=True,
        queryset=FaixaEtaria.objects.all()
    )
    medicao_uuid = serializers.SerializerMethodField()
    medicao_alterado_em = serializers.SerializerMethodField()

    def get_medicao_alterado_em(self, obj):
        if obj.medicao.alterado_em:
            return datetime.strftime(obj.medicao.alterado_em, '%d/%m/%Y, às %H:%M:%S')

    def get_medicao_uuid(self, obj):
        return obj.medicao.uuid

    class Meta:
        model = ValorMedicao
        exclude = ('id', 'medicao',)


class MedicaoCreateUpdateSerializer(serializers.ModelSerializer):
    solicitacao_medicao_inicial = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=SolicitacaoMedicaoInicial.objects.all()
    )
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='nome',
        required=False,
        queryset=PeriodoEscolar.objects.all(),
    )
    grupo = serializers.SlugRelatedField(
        slug_field='nome',
        required=False,
        queryset=GrupoMedicao.objects.all(),
    )
    valores_medicao = ValorMedicaoCreateUpdateSerializer(many=True, required=False)

    def create(self, validated_data):
        validated_data['criado_por'] = self.context['request'].user
        valores_medicao_dict = validated_data.pop('valores_medicao', None)

        if validated_data.get('periodo_escolar', '') and validated_data.get('grupo', ''):
            medicao, created = Medicao.objects.get_or_create(
                solicitacao_medicao_inicial=validated_data.get('solicitacao_medicao_inicial', ''),
                periodo_escolar=validated_data.get('periodo_escolar', ''),
                grupo=validated_data.get('grupo', '')
            )
        elif validated_data.get('periodo_escolar', '') and not validated_data.get('grupo', ''):
            medicao, created = Medicao.objects.get_or_create(
                solicitacao_medicao_inicial=validated_data.get('solicitacao_medicao_inicial', ''),
                periodo_escolar=validated_data.get('periodo_escolar', ''),
                grupo=None
            )
        else:
            medicao, created = Medicao.objects.get_or_create(
                solicitacao_medicao_inicial=validated_data.get('solicitacao_medicao_inicial', ''),
                grupo=validated_data.get('grupo', ''),
                periodo_escolar=None
            )
        medicao.save()

        for valor_medicao in valores_medicao_dict:
            dia = int(valor_medicao.get('dia', ''))
            mes = int(medicao.solicitacao_medicao_inicial.mes)
            ano = int(medicao.solicitacao_medicao_inicial.ano)
            semana = ValorMedicao.get_week_of_month(ano, mes, dia)
            ValorMedicao.objects.update_or_create(
                medicao=medicao,
                dia=valor_medicao.get('dia', ''),
                semana=semana,
                nome_campo=valor_medicao.get('nome_campo', ''),
                categoria_medicao=valor_medicao.get('categoria_medicao', ''),
                tipo_alimentacao=valor_medicao.get('tipo_alimentacao', None),
                faixa_etaria=valor_medicao.get('faixa_etaria', None),
                defaults={
                    'medicao': medicao,
                    'dia': valor_medicao.get('dia', ''),
                    'semana': semana,
                    'valor': valor_medicao.get('valor', ''),
                    'nome_campo': valor_medicao.get('nome_campo', ''),
                    'categoria_medicao': valor_medicao.get('categoria_medicao', ''),
                    'tipo_alimentacao': valor_medicao.get('tipo_alimentacao', None),
                    'faixa_etaria': valor_medicao.get('faixa_etaria', None),
                }
            )

        return medicao

    def update(self, instance, validated_data):  # noqa C901
        user = self.context['request'].user
        acao = instance.workflow_class.MEDICAO_CORRIGIDA_PELA_UE
        valores = validated_data.get('valores_medicao', None)
        if instance.status in [acao, instance.workflow_class.MEDICAO_CORRECAO_SOLICITADA]:
            log_alteracoes_escola_corrige_periodo(user, instance, acao, valores)

        valores_medicao_dict = validated_data.pop('valores_medicao', None)

        if valores_medicao_dict:
            for valor_medicao in valores_medicao_dict:
                dia = int(valor_medicao.get('dia', ''))
                mes = int(instance.solicitacao_medicao_inicial.mes)
                ano = int(instance.solicitacao_medicao_inicial.ano)
                semana = ValorMedicao.get_week_of_month(ano, mes, dia)
                ValorMedicao.objects.update_or_create(
                    medicao=instance,
                    dia=valor_medicao.get('dia', ''),
                    semana=semana,
                    nome_campo=valor_medicao.get('nome_campo', ''),
                    categoria_medicao=valor_medicao.get('categoria_medicao', ''),
                    tipo_alimentacao=valor_medicao.get('tipo_alimentacao', None),
                    faixa_etaria=valor_medicao.get('faixa_etaria', None),
                    defaults={
                        'medicao': instance,
                        'dia': valor_medicao.get('dia', ''),
                        'semana': semana,
                        'valor': valor_medicao.get('valor', ''),
                        'nome_campo': valor_medicao.get('nome_campo', ''),
                        'categoria_medicao': valor_medicao.get('categoria_medicao', ''),
                        'tipo_alimentacao': valor_medicao.get('tipo_alimentacao', None),
                        'faixa_etaria': valor_medicao.get('faixa_etaria', None),
                    }
                )
        eh_observacao = self.context['request'].data.get('eh_observacao', )
        if not eh_observacao:
            instance.valores_medicao.filter(valor=-1).delete()
        instance.alterado_em = datetime.now()
        instance.save()
        if not instance.valores_medicao.all().exists():
            instance.delete()

        return instance

    class Meta:
        model = Medicao
        exclude = ('id', 'criado_por',)
