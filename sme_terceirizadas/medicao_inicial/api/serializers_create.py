import calendar
import json
from datetime import date, datetime

import environ
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from sme_terceirizadas.cardapio.models import TipoAlimentacao
from sme_terceirizadas.dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile, update_instance_from_dict
from sme_terceirizadas.dados_comuns.validators import deve_ter_extensao_xls_xlsx_pdf
from sme_terceirizadas.escola.api.serializers_create import AlunoPeriodoParcialCreateSerializer
from sme_terceirizadas.escola.models import (
    Aluno,
    AlunoPeriodoParcial,
    DiretoriaRegional,
    Escola,
    FaixaEtaria,
    PeriodoEscolar,
    TipoUnidadeEscolar
)
from sme_terceirizadas.medicao_inicial.models import (
    AlimentacaoLancamentoEspecial,
    CategoriaMedicao,
    DiaSobremesaDoce,
    GrupoMedicao,
    Medicao,
    OcorrenciaMedicaoInicial,
    PermissaoLancamentoEspecial,
    Responsavel,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)
from sme_terceirizadas.perfil.models import Usuario

from ...dados_comuns.constants import DIRETOR_UE
from ...inclusao_alimentacao.models import InclusaoAlimentacaoContinua
from ..utils import log_alteracoes_escola_corrige_periodo
from ..validators import (
    validate_lancamento_alimentacoes_medicao,
    validate_lancamento_dietas,
    validate_lancamento_inclusoes,
    validate_lancamento_kit_lanche,
    validate_lanche_emergencial,
    validate_solicitacoes_etec,
    validate_solicitacoes_programas_e_projetos
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
    tipos_contagem_alimentacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TipoContagemAlimentacao.objects.all(),
        many=True
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
        tipos_contagem_alimentacao = validated_data.pop('tipos_contagem_alimentacao', [])
        solicitacao = SolicitacaoMedicaoInicial.objects.create(**validated_data)
        solicitacao.tipos_contagem_alimentacao.set(tipos_contagem_alimentacao)
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

    def valida_finalizar_medicao_emef_emei(self, instance: SolicitacaoMedicaoInicial) -> None:
        if not instance.escola.eh_emef_emei_cieja:
            return

        lista_erros = []

        if instance.status == SolicitacaoMedicaoInicial.workflow_class.MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE:
            lista_erros = validate_lancamento_alimentacoes_medicao(instance, lista_erros)
            lista_erros = validate_lancamento_inclusoes(instance, lista_erros)
            lista_erros = validate_lancamento_dietas(instance, lista_erros)
            lista_erros = validate_lancamento_kit_lanche(instance, lista_erros)
            lista_erros = validate_lanche_emergencial(instance, lista_erros)
            lista_erros = validate_solicitacoes_etec(instance, lista_erros)
            lista_erros = validate_solicitacoes_programas_e_projetos(instance, lista_erros)

        if lista_erros:
            raise ValidationError(lista_erros)

    def cria_valores_medicao_logs_alunos_matriculados_emef_emei(self, instance: SolicitacaoMedicaoInicial) -> None:
        escola = instance.escola
        valores_medicao_a_criar = []
        logs_do_mes = escola.logs_alunos_matriculados_por_periodo.filter(
            criado_em__month=instance.mes,
            criado_em__year=instance.ano,
            tipo_turma='REGULAR'
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

    def checa_se_existe_ao_menos_um_log_quantidade_maior_que_0(
            self, categoria: CategoriaMedicao, logs_do_mes: QuerySet, periodo_escolar: str) -> bool:
        if categoria == CategoriaMedicao.objects.get(
            nome='DIETA ESPECIAL - TIPO A - ENTERAL / RESTRIÇÃO DE AMINOÁCIDOS'
        ):
            if not logs_do_mes.filter(
                classificacao__nome__in=['Tipo A ENTERAL', 'Tipo A RESTRIÇÃO DE AMINOÁCIDOS'],
                periodo_escolar__nome=periodo_escolar,
                quantidade__gt=0
            ).exists():
                return True
        else:
            if not logs_do_mes.filter(
                classificacao__nome__icontains=categoria.nome.split(' - ')[1],
                periodo_escolar__nome=periodo_escolar,
                quantidade__gt=0
            ).exclude(
                classificacao__nome__icontains='enteral'
            ).exclude(
                classificacao__nome__icontains='aminoácidos'
            ).exists():
                return True
        return False

    def retorna_valor_para_log_dieta_autorizada(
            self, categoria: CategoriaMedicao, logs_do_mes: QuerySet, periodo_escolar: str, dia: int) -> int:
        if categoria == CategoriaMedicao.objects.get(
            nome='DIETA ESPECIAL - TIPO A - ENTERAL / RESTRIÇÃO DE AMINOÁCIDOS'
        ):
            log_enteral = logs_do_mes.filter(
                classificacao__nome__icontains='enteral',
                periodo_escolar__nome=periodo_escolar,
                data__day=dia
            ).first()
            log_restricao_aminoacidos = logs_do_mes.filter(
                classificacao__nome__icontains='aminoácidos',
                periodo_escolar__nome=periodo_escolar,
                data__day=dia
            ).first()
            valor = ((log_enteral.quantidade if log_enteral else 0) +
                     (log_restricao_aminoacidos.quantidade if log_restricao_aminoacidos else 0))
        else:
            log = logs_do_mes.filter(
                classificacao__nome__icontains=categoria.nome.split(' - ')[1],
                periodo_escolar__nome=periodo_escolar,
                data__day=dia
            ).exclude(
                classificacao__nome__icontains='enteral'
            ).exclude(
                classificacao__nome__icontains='aminoácidos'
            ).first()
            valor = log.quantidade if log else 0
        return valor

    def cria_valores_medicao_logs_dietas_autorizadas_emef_emei(self, instance: SolicitacaoMedicaoInicial) -> None:
        escola = instance.escola
        valores_medicao_a_criar = []
        logs_do_mes = escola.logs_dietas_autorizadas.filter(
            data__month=instance.mes,
            data__year=instance.ano
        )
        categorias = CategoriaMedicao.objects.filter(nome__icontains='dieta')
        quantidade_dias_mes = calendar.monthrange(int(instance.ano), int(instance.mes))[1]
        for dia in range(1, quantidade_dias_mes + 1):
            for categoria in categorias:
                for periodo_escolar in escola.periodos_escolares_com_alunos:
                    medicao = instance.medicoes.get(periodo_escolar__nome=periodo_escolar)
                    if self.checa_se_existe_ao_menos_um_log_quantidade_maior_que_0(
                            categoria, logs_do_mes, periodo_escolar):
                        continue
                    if not medicao.valores_medicao.filter(
                        categoria_medicao=categoria,
                        dia=f'{dia:02d}',
                        nome_campo='dietas_autorizadas',
                    ).exists():
                        valor = self.retorna_valor_para_log_dieta_autorizada(
                            categoria, logs_do_mes, periodo_escolar, dia)
                        valor_medicao = ValorMedicao(
                            medicao=medicao,
                            categoria_medicao=categoria,
                            dia=f'{dia:02d}',
                            nome_campo='dietas_autorizadas',
                            valor=valor
                        )
                        valores_medicao_a_criar.append(valor_medicao)
        ValorMedicao.objects.bulk_create(valores_medicao_a_criar)

    def retorna_medicao_por_nome_grupo(self, instance: SolicitacaoMedicaoInicial, nome_grupo: str) -> Medicao:
        try:
            medicao = instance.medicoes.get(grupo__nome=nome_grupo)
        except Medicao.DoesNotExist:
            grupo = GrupoMedicao.objects.get(nome=nome_grupo)
            medicao = Medicao.objects.create(
                solicitacao_medicao_inicial=instance,
                grupo=grupo
            )
        return medicao

    def retorna_numero_alunos_dia(self, inclusao: InclusaoAlimentacaoContinua, data: date) -> int:
        dia_semana = data.weekday()
        numero_alunos = 0
        for quantidade_periodo in inclusao.quantidades_periodo.filter(
            dias_semana__icontains=dia_semana,
            cancelado=False
        ):
            numero_alunos += quantidade_periodo.numero_alunos
        return numero_alunos

    def cria_valor_medicao(self, numero_alunos: int, medicao: Medicao, categoria: CategoriaMedicao, dia: int,
                           nome_campo: str, valores_medicao_a_criar: list) -> list:
        if numero_alunos > 0:
            valor_medicao = ValorMedicao(
                medicao=medicao,
                categoria_medicao=categoria,
                dia=f'{dia:02d}',
                nome_campo=nome_campo,
                valor=numero_alunos
            )
            valores_medicao_a_criar.append(valor_medicao)
        return valores_medicao_a_criar

    def cria_valores_medicao_logs_numero_alunos_inclusoes_continuas(
            self, instance: SolicitacaoMedicaoInicial, inclusoes_continuas: QuerySet, quantidade_dias_mes: int,
            nome_motivo: str, nome_grupo: str) -> None:
        if not inclusoes_continuas.filter(motivo__nome__icontains=nome_motivo).exists():
            return
        categoria = CategoriaMedicao.objects.get(nome='ALIMENTAÇÃO')
        medicao = self.retorna_medicao_por_nome_grupo(instance, nome_grupo)
        valores_medicao_a_criar = []
        for dia in range(1, quantidade_dias_mes + 1):
            data = date(year=int(instance.ano), month=int(instance.mes), day=dia)
            numero_alunos = 0
            for inclusao in inclusoes_continuas.filter(motivo__nome__icontains=nome_motivo):
                if not (inclusao.data_inicial <= data <= inclusao.data_final):
                    continue
                if medicao.valores_medicao.filter(
                    categoria_medicao=categoria,
                    dia=f'{dia:02d}',
                    nome_campo='numero_de_alunos',
                ).exists():
                    continue
                numero_alunos += self.retorna_numero_alunos_dia(inclusao, data)
            valores_medicao_a_criar = self.cria_valor_medicao(
                numero_alunos, medicao, categoria, dia, 'numero_de_alunos', valores_medicao_a_criar)
        ValorMedicao.objects.bulk_create(valores_medicao_a_criar)

    def cria_valores_medicao_logs_numero_alunos_inclusoes_continuas_emef_emei(
            self, instance: SolicitacaoMedicaoInicial) -> None:
        escola = instance.escola
        quantidade_dias_mes = calendar.monthrange(int(instance.ano), int(instance.mes))[1]
        ultimo_dia_mes = date(year=int(instance.ano), month=int(instance.mes), day=quantidade_dias_mes)
        primeiro_dia_mes = date(year=int(instance.ano), month=int(instance.mes), day=1)
        inclusoes_continuas = escola.inclusoes_alimentacao_continua.filter(
            status='CODAE_AUTORIZADO',
            data_inicial__lte=ultimo_dia_mes,
            data_final__gte=primeiro_dia_mes
        )
        if not inclusoes_continuas.count():
            return
        self.cria_valores_medicao_logs_numero_alunos_inclusoes_continuas(
            instance, inclusoes_continuas, quantidade_dias_mes, 'Programas/Projetos', 'Programas e Projetos')
        self.cria_valores_medicao_logs_numero_alunos_inclusoes_continuas(
            instance, inclusoes_continuas, quantidade_dias_mes, 'ETEC', 'ETEC')

    def cria_valores_medicao_logs_numero_alunos_emef_emei(self, instance: SolicitacaoMedicaoInicial) -> None:
        self.cria_valores_medicao_logs_numero_alunos_inclusoes_continuas_emef_emei(instance)

    def cria_valores_medicao_kit_lanches_emef_emei(self, instance, kits_lanche, kits_lanche_unificado):
        valores_medicao_a_criar = []
        medicao = self.retorna_medicao_por_nome_grupo(instance, 'Solicitações de Alimentação')
        categoria = CategoriaMedicao.objects.get(nome='SOLICITAÇÕES DE ALIMENTAÇÃO')
        quantidade_dias_mes = calendar.monthrange(int(instance.ano), int(instance.mes))[1]
        for dia in range(1, quantidade_dias_mes + 1):
            if medicao.valores_medicao.filter(
                categoria_medicao=categoria,
                dia=f'{dia:02d}',
                nome_campo='kit_lanche',
            ).exists():
                continue
            total_dia = 0
            for kit_lanche in kits_lanche.filter(solicitacao_kit_lanche__data__day=dia):
                total_dia += kit_lanche.quantidade_alimentacoes
            for kit_lanche in kits_lanche_unificado.filter(
                    solicitacao_unificada__solicitacao_kit_lanche__data__day=dia):
                total_dia += kit_lanche.total_kit_lanche
            valores_medicao_a_criar = self.cria_valor_medicao(
                total_dia, medicao, categoria, dia, 'kit_lanche', valores_medicao_a_criar)
        ValorMedicao.objects.bulk_create(valores_medicao_a_criar)

    def cria_valores_medicao_logs_kit_lanche_lanches_emergenciais_emef_emei(
            self, instance: SolicitacaoMedicaoInicial) -> None:
        escola = instance.escola
        kits_lanche = escola.kit_lanche_solicitacaokitlancheavulsa_rastro_escola.filter(
            status='CODAE_AUTORIZADO',
            solicitacao_kit_lanche__data__month=instance.mes,
            solicitacao_kit_lanche__data__year=instance.ano
        )
        kits_lanche_unificado = escola.escolaquantidade_set.filter(
            solicitacao_unificada__status='CODAE_AUTORIZADO',
            solicitacao_unificada__solicitacao_kit_lanche__data__month=instance.mes,
            solicitacao_unificada__solicitacao_kit_lanche__data__year=instance.ano,
            cancelado=False
        )
        lanches_emergenciais = escola.alteracaocardapio_set.filter(
            motivo__nome='Lanche Emergencial',
            status='CODAE_AUTORIZADO',
            datas_intervalo__data__month=instance.mes,
            datas_intervalo__data__year=instance.ano,
            datas_intervalo__cancelado=False
        )

        if not kits_lanche.exists() and not kits_lanche_unificado.exists() and not lanches_emergenciais.exists():
            return

        self.cria_valores_medicao_kit_lanches_emef_emei(instance, kits_lanche, kits_lanche_unificado)

    def cria_valores_medicao_logs_emef_emei(self, instance: SolicitacaoMedicaoInicial) -> None:
        if not instance.escola.eh_emef_emei_cieja or instance.logs_salvos:
            return

        self.cria_valores_medicao_logs_alunos_matriculados_emef_emei(instance)
        self.cria_valores_medicao_logs_dietas_autorizadas_emef_emei(instance)
        self.cria_valores_medicao_logs_numero_alunos_emef_emei(instance)
        self.cria_valores_medicao_logs_kit_lanche_lanches_emergenciais_emef_emei(instance)

        instance.logs_salvos = True
        instance.save()

    def update(self, instance, validated_data):
        self._check_user_permission()
        self._update_instance_fields(instance, validated_data)
        self._update_responsaveis(instance)
        self._update_alunos(instance, validated_data)
        self._update_tipos_contagem_alimentacao(instance)
        self._process_anexos(instance)
        self._finaliza_medicao_se_necessario(instance, validated_data)
        return instance

    def _check_user_permission(self):
        if self.context['request'].user.vinculo_atual.perfil.nome != DIRETOR_UE:
            raise PermissionDenied('Você não tem permissão para executar essa ação.')

    def _update_instance_fields(self, instance, validated_data):
        update_instance_from_dict(instance, validated_data, save=True)

    def _update_responsaveis(self, instance):
        responsaveis_dict = self.context['request'].data.get('responsaveis')
        if responsaveis_dict:
            instance.responsaveis.all().delete()
            for responsavel_data in json.loads(responsaveis_dict):
                Responsavel.objects.create(
                    solicitacao_medicao_inicial=instance, **responsavel_data
                )

    def _update_alunos(self, instance, validated_data):
        alunos_uuids_dict = self.context['request'].data.get('alunos_periodo_parcial')
        if alunos_uuids_dict:
            instance.alunos_periodo_parcial.all().delete()
            escola_associada = validated_data.get('escola')
            for aluno_uuid in json.loads(alunos_uuids_dict):
                AlunoPeriodoParcial.objects.create(
                    solicitacao_medicao_inicial=instance,
                    aluno=Aluno.objects.get(uuid=aluno_uuid),
                    escola=escola_associada
                )

    def _update_tipos_contagem_alimentacao(self, instance):
        tipos_contagem_alimentacao = self._get_tipos_contagem_alimentacao_from_request()
        if tipos_contagem_alimentacao:
            tipos_contagem_alimentacao = TipoContagemAlimentacao.objects.filter(uuid__in=tipos_contagem_alimentacao)
            instance.tipos_contagem_alimentacao.set(tipos_contagem_alimentacao)

    def _get_tipos_contagem_alimentacao_from_request(self):
        if 'tipos_contagem_alimentacao[]' in self.context['request'].data:
            return self.context['request'].data.getlist('tipos_contagem_alimentacao[]')
        return self.context['request'].data.get('tipos_contagem_alimentacao')

    def _process_anexos(self, instance):
        anexos_string = self.context['request'].data.get('anexos')
        if anexos_string:
            for anexo in json.loads(anexos_string):
                if '.pdf' in anexo['nome']:
                    arquivo = convert_base64_to_contentfile(anexo['base64'])
                    OcorrenciaMedicaoInicial.objects.create(
                        solicitacao_medicao_inicial=instance,
                        ultimo_arquivo=arquivo,
                        nome_ultimo_arquivo=anexo.get('nome')
                    )

    def _finaliza_medicao_se_necessario(self, instance, validated_data):
        key_com_ocorrencias = validated_data.get('com_ocorrencias', None)
        if key_com_ocorrencias is not None and self.context['request'].data.get('finaliza_medicao'):
            self.cria_valores_medicao_logs_emef_emei(instance)
            self.valida_finalizar_medicao_emef_emei(instance)
            instance.ue_envia(user=self.context['request'].user)
            if hasattr(instance, 'ocorrencia'):
                instance.ocorrencia.ue_envia(user=self.context['request'].user)
            for medicao in instance.medicoes.all():
                medicao.ue_envia(user=self.context['request'].user)

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


class PermissaoLancamentoEspecialCreateUpdateSerializer(serializers.ModelSerializer):
    escola = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Escola.objects.all()
    )
    periodo_escolar = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=PeriodoEscolar.objects.all()
    )
    alimentacoes_lancamento_especial = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=AlimentacaoLancamentoEspecial.objects.all(),
        many=True
    )
    diretoria_regional = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=DiretoriaRegional.objects.all()
    )
    criado_por = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Usuario.objects.all()
    )

    def validate(self, attrs):
        data_inicial = attrs.get('data_inicial', None)
        data_final = attrs.get('data_final', None)
        if data_inicial and data_final and data_inicial > data_final:
            raise ValidationError('data inicial não pode ser maior que data final')

        return attrs

    class Meta:
        model = PermissaoLancamentoEspecial
        fields = '__all__'
