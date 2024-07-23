from django.db import connection
from django.core.paginator import Paginator, EmptyPage

SQL_RELATORIO_CONTROLE_RESTOS = """
    with medicao as (
        select mis.escola_id,
            (mis.ano || '-' || mis.mes || '-' || miv.dia)::date as data_medicao,
            ep.nome as periodo_nome,
            miv.tipo_alimentacao_id,
            sum(case when miv.nome_campo = 'frequencia' then miv.valor::numeric else 0 end) as frequencia,
            sum(case when miv.tipo_alimentacao_id is not null then miv.valor::numeric else 0 end) as num_refeicoes
        from medicao_inicial_solicitacaomedicaoinicial mis
        join medicao_inicial_medicao mim on mim.solicitacao_medicao_inicial_id = mis.id
        join medicao_inicial_valormedicao miv on miv.medicao_id = mim.id
        join escola_periodoescolar ep on ep.id = mim.periodo_escolar_id
        where (mis.ano || '-' || mis.mes || '-' || miv.dia)::date between %s::date and %s::date
            and miv.tipo_alimentacao_id is not null
        group by 1, 2, 3, 4
    ),
    sobras as (
        select COUNT(*) as quantidade_distribuida,
            SUM(dcs.peso_alimento) as peso_alimento_total,
            SUM(dcs.peso_recipiente) as peso_recipiente_total,
            dcs.escola_id,
            dcs.periodo,
            dcs.data_medicao,
            dcs.tipo_alimento_id
        from desperdicio_controlesobras dcs	
        where dcs.data_medicao between %s::date and %s::date
        group by 4, 5, 6, 7
    ),
    relatorio as (
        select 
            dre.nome as dre_nome, 
            ee.nome as escola_nome,
            dcr.data_medicao, 
            dcr.periodo,
            dcr.cardapio,
            cta.nome as tipo_alimentacao_nome,
            dcr.resto_predominante,
            s.quantidade_distribuida,
            pta.nome as tipo_alimento_nome,
            dcr.peso_resto,
            m.num_refeicoes,
            CASE WHEN m.frequencia = 0 THEN 0 ELSE (dcr.peso_resto / m.frequencia::numeric) END as resto_per_capita,
            CASE WHEN s.quantidade_distribuida = 0 THEN 0 ELSE (dcr.peso_resto / s.quantidade_distribuida) END as percent_resto,
            case when s.peso_alimento_total is null then null
                else 
                    cast(((s.peso_alimento_total - dcr.peso_resto) * 100 / (s.peso_alimento_total + s.peso_recipiente_total)) as numeric(10,2))
                end as aceitabilidade,
            dcr.observacoes
        from desperdicio_controlerestos dcr
        join medicao m on m.escola_id = dcr.escola_id 
            and m.tipo_alimentacao_id = dcr.tipo_alimentacao_id
            and m.data_medicao = dcr.data_medicao
            and case dcr.periodo 
                WHEN 'M' THEN 'MANHA'
                WHEN 'T' THEN 'TARDE'
                WHEN 'I' THEN 'INTEGRAL'
            end = m.periodo_nome
        left join sobras s on s.escola_id = dcr.escola_id 
            and s.data_medicao = dcr.data_medicao
            and s.periodo = dcr.periodo
        left join produto_tipoalimento pta on pta.id = s.tipo_alimento_id  
        join escola_escola ee on ee.id = dcr.escola_id
        join escola_diretoriaregional dre on dre.id = ee.diretoria_regional_id
        join cardapio_tipoalimentacao cta on cta.id = dcr.tipo_alimentacao_id
        where dcr.data_medicao between %s::date and %s::date
        [EXTRA_WHERE_CLAUSES]
        order by 1, 2, 3, 4
    )
    select 
        r.*,
        (
            select dc.descricao 
            from desperdicio_classificacao dc 
            where r.percent_resto <= dc.valor and dc.tipo = 'CR'
            order by valor
            limit 1
        ) as classificacao
    from relatorio r
"""

SQL_RELATORIO_CONTROLE_SOBRAS = """
    with medicao as (
        select mis.escola_id, (mis.ano || '-' || mis.mes || '-' || miv.dia)::date as data_medicao,
            case
                when miv.tipo_alimentacao_id is not null then miv.tipo_alimentacao_id
                when miv.nome_campo = 'repeticao_refeicao' then 2
                when miv.nome_campo = 'repeticao_sobremesa' then 4
            else null end as tipo_alimentacao_id,
            ep.nome as periodo_nome,
            sum(case when miv.nome_campo like 'repeticao_%%' then 0 else miv.valor::numeric end) as total_primeira_oferta,
            sum(case when miv.nome_campo like 'repeticao_%%' then miv.valor::numeric else 0 end) as total_repeticao,
            sum(miv.valor::numeric) as total_refeicao
        from medicao_inicial_solicitacaomedicaoinicial mis
        join medicao_inicial_medicao mim on mim.solicitacao_medicao_inicial_id = mis.id
        join medicao_inicial_valormedicao miv on miv.medicao_id = mim.id
        join escola_periodoescolar ep on ep.id = mim.periodo_escolar_id
        where (miv.tipo_alimentacao_id is not null or miv.nome_campo ilike ('repeticao_%%'))
            and (mis.ano || '-' || mis.mes || '-' || miv.dia)::date between %s::date and %s::date
        group by 1, 2, 3, 4
    ),
    frequencia as (
        select mis.escola_id, (mis.ano || '-' || mis.mes || '-' || miv.dia)::date as data_medicao, sum(miv.valor::numeric) as frequencia
        from medicao_inicial_solicitacaomedicaoinicial mis
        join medicao_inicial_medicao mim on mim.solicitacao_medicao_inicial_id = mis.id
        join medicao_inicial_valormedicao miv on miv.medicao_id = mim.id
        join escola_periodoescolar ep on ep.id = mim.periodo_escolar_id
        where miv.nome_campo = 'frequencia'
            and (mis.ano || '-' || mis.mes || '-' || miv.dia)::date between %s::date and %s::date
        group by 1, 2
    ),
    sobras as (
        select cs.escola_id, cs.data_medicao, cs.tipo_alimentacao_id, 
            ta.nome as tipo_alimento_nome, cs.periodo,
            cs.peso_recipiente, pt.nome as tipo_recipiente_nome,
            sum(cs.peso_alimento - cs.peso_recipiente) as peso_alimento,
            sum(cs.peso_sobra - cs.peso_recipiente) as peso_sobra
        from desperdicio_controlesobras cs
        join produto_tipoalimento ta on ta.id = cs.tipo_alimento_id
        join escola_escola e on e.id = cs.escola_id
        join produto_tiporecipiente pt on pt.id = cs.tipo_recipiente_id
        where cs.data_medicao between %s::date and %s::date
        [EXTRA_WHERE_CLAUSES]
        group by 1, 2, 3, 4, 5, 6, 7
    ),
    relatorio as (
	    select m.data_medicao,
	        s.periodo,
	        s.tipo_recipiente_nome,
	        s.peso_recipiente,
	        dre.nome as dre_nome,
	        ee.nome as escola_nome,
	        ta.nome as tipo_alimentacao_nome,
	        s.tipo_alimento_nome,
            coalesce(s.peso_alimento, 0) as peso_alimento,
	        coalesce(s.peso_sobra, 0) as peso_sobra,
	        coalesce((s.peso_alimento - s.peso_sobra), 0) as quantidade_distribuida,
	        coalesce(f.frequencia, 0) as frequencia,
	        coalesce(m.total_primeira_oferta, 0) as total_primeira_oferta,
	        coalesce(m.total_repeticao, 0) as total_repeticao,
	        CASE WHEN (s.peso_alimento - s.peso_sobra) = 0 THEN 0 ELSE (s.peso_sobra / (s.peso_alimento - s.peso_sobra)) * 100 END as percentual_sobra,
	        CASE WHEN f.frequencia = 0 THEN 0 ELSE (s.peso_sobra / f.frequencia) END as media_por_aluno,
	        CASE WHEN m.total_refeicao = 0 THEN 0 ELSE (s.peso_sobra / m.total_refeicao) END as media_por_refeicao
	    from medicao m
	    join escola_escola ee on ee.id = m.escola_id
	    join escola_diretoriaregional dre on dre.id = ee.diretoria_regional_id
	    join cardapio_tipoalimentacao ta on ta.id = m.tipo_alimentacao_id
	    join sobras s on s.escola_id = m.escola_id 
	    	and s.data_medicao = m.data_medicao 
	    	and s.tipo_alimentacao_id = m.tipo_alimentacao_id
	    	and case s.periodo 
				WHEN 'M' THEN 'MANHA'
		        WHEN 'T' THEN 'TARDE'
	    	    WHEN 'I' THEN 'INTEGRAL'
	    	end = m.periodo_nome
	    join frequencia f on f.escola_id = m.escola_id and f.data_medicao = m.data_medicao and f.escola_id = s.escola_id and f.data_medicao = s.data_medicao
	    order by 1, 3, 4, 6	
 	)
 	select 
        r.*,
        (
            select dc.descricao from desperdicio_classificacao dc 
            where r.percentual_sobra <= dc.valor and dc.tipo = 'CS'
            order by valor
            limit 1
        ) as classificacao
    from relatorio r
"""

SQL_RELATORIO_CONTROLE_SOBRAS_BRUTO = """
    with medicao as (
        select mis.escola_id, (mis.ano || '-' || mis.mes || '-' || miv.dia)::date as data_medicao,
            case
                when miv.tipo_alimentacao_id is not null then miv.tipo_alimentacao_id
                when miv.nome_campo = 'repeticao_refeicao' then 2
                when miv.nome_campo = 'repeticao_sobremesa' then 4
            else null end as tipo_alimentacao_id,
            ep.nome as periodo_nome,
            sum(case when miv.nome_campo like 'repeticao_%%' then 0 else miv.valor::numeric end) as total_primeira_oferta,
            sum(case when miv.nome_campo like 'repeticao_%%' then miv.valor::numeric else 0 end) as total_repeticao,
            sum(miv.valor::numeric) as total_refeicao
        from medicao_inicial_solicitacaomedicaoinicial mis
        join medicao_inicial_medicao mim on mim.solicitacao_medicao_inicial_id = mis.id
        join medicao_inicial_valormedicao miv on miv.medicao_id = mim.id
        join escola_periodoescolar ep on ep.id = mim.periodo_escolar_id
        where (miv.tipo_alimentacao_id is not null or miv.nome_campo ilike ('repeticao_%%'))
            and (mis.ano || '-' || mis.mes || '-' || miv.dia)::date between %s::date and %s::date
        group by 1, 2, 3, 4
    ),
    frequencia as (
        select mis.escola_id, (mis.ano || '-' || mis.mes || '-' || miv.dia)::date as data_medicao, sum(miv.valor::numeric) as frequencia
        from medicao_inicial_solicitacaomedicaoinicial mis
        join medicao_inicial_medicao mim on mim.solicitacao_medicao_inicial_id = mis.id
        join medicao_inicial_valormedicao miv on miv.medicao_id = mim.id
        join escola_periodoescolar ep on ep.id = mim.periodo_escolar_id
        where miv.nome_campo = 'frequencia'
            and (mis.ano || '-' || mis.mes || '-' || miv.dia)::date between %s::date and %s::date
        group by 1, 2
    ),
    sobras as (
        select cs.escola_id, cs.data_medicao, cs.tipo_alimentacao_id, 
            ta.nome as tipo_alimento_nome, cs.periodo,
            cs.peso_recipiente, pt.nome as tipo_recipiente_nome,
            cs.especificar,
            cs.peso_alimento - cs.peso_recipiente as peso_alimento,
            cs.peso_sobra - cs.peso_recipiente as peso_sobra
        from desperdicio_controlesobras cs
        join produto_tipoalimento ta on ta.id = cs.tipo_alimento_id
        join escola_escola e on e.id = cs.escola_id
        join produto_tiporecipiente pt on pt.id = cs.tipo_recipiente_id
        where cs.data_medicao between %s::date and %s::date
        [EXTRA_WHERE_CLAUSES]
    ),
    relatorio as (
	    select
	        ee.nome as escola_nome,
	        dre.nome as dre_nome,
            m.data_medicao,
	        s.periodo,
            ta.nome as tipo_alimentacao_nome,
	        s.tipo_alimento_nome,
            s.especificar,
	        s.tipo_recipiente_nome,
	        coalesce(s.peso_recipiente, 0) as peso_recipiente,
            coalesce(s.peso_alimento, 0) + coalesce(s.peso_recipiente, 0) as peso_alimento_pronto_com_recipiente,
            coalesce(s.peso_sobra, 0) + coalesce(s.peso_recipiente, 0) as peso_sobra_com_recipiente,
            coalesce(s.peso_alimento, 0) as peso_alimento,
	        coalesce(s.peso_sobra, 0) as peso_sobra,
	        coalesce((s.peso_alimento - s.peso_sobra), 0) as peso_distribuida,
	        coalesce(f.frequencia, 0) as frequencia,
	        coalesce(m.total_primeira_oferta, 0) as total_primeira_oferta,
	        coalesce(m.total_repeticao, 0) as total_repeticao,
	        CASE WHEN (s.peso_alimento - s.peso_sobra) = 0 THEN 0 ELSE (s.peso_sobra / (s.peso_alimento - s.peso_sobra)) * 100 END as percentual_sobra,
	        CASE WHEN f.frequencia = 0 THEN 0 ELSE (s.peso_sobra / f.frequencia) END as media_por_aluno,
	        CASE WHEN m.total_refeicao = 0 THEN 0 ELSE (s.peso_sobra / m.total_refeicao) END as media_por_refeicao
	    from medicao m
	    join escola_escola ee on ee.id = m.escola_id
	    join escola_diretoriaregional dre on dre.id = ee.diretoria_regional_id
	    join cardapio_tipoalimentacao ta on ta.id = m.tipo_alimentacao_id
	    join sobras s on s.escola_id = m.escola_id 
	    	and s.data_medicao = m.data_medicao 
	    	and s.tipo_alimentacao_id = m.tipo_alimentacao_id
	    	and case s.periodo 
				WHEN 'M' THEN 'MANHA'
		        WHEN 'T' THEN 'TARDE'
	    	    WHEN 'I' THEN 'INTEGRAL'
	    	end = m.periodo_nome
	    join frequencia f on f.escola_id = m.escola_id and f.data_medicao = m.data_medicao and f.escola_id = s.escola_id and f.data_medicao = s.data_medicao
	    order by 1, 3, 4, 6	
 	)
 	select 
        r.*,
        (
            select dc.descricao from desperdicio_classificacao dc 
            where r.percentual_sobra <= dc.valor and dc.tipo = 'CS'
            order by valor
            limit 1
        ) as classificacao
    from relatorio r
"""


def obtem_dados_relatorio_controle_restos(form_data, user):
    extra_where_clauses = ""

    data_inicial = form_data['data_inicial'].strftime('%Y-%m-%d')
    data_final = form_data['data_final'].strftime('%Y-%m-%d')

    extra_arguments = [
        data_inicial, data_final,
        data_inicial, data_final,
        data_inicial, data_final
    ]

    if user.tipo_usuario == 'escola':
        extra_where_clauses = "AND dcr.escola_id = %s"
        extra_arguments.append(user.vinculo_atual.instituicao.id)
    elif form_data['escola']:
        extra_where_clauses = "AND dcr.escola_id = %s"
        extra_arguments.append(form_data['escola'].id)
    elif form_data['dre']:
        extra_where_clauses = "AND ee.diretoria_regional_id = %s"
        extra_arguments.append(form_data['dre'].id)

    sql = SQL_RELATORIO_CONTROLE_RESTOS.replace('[EXTRA_WHERE_CLAUSES]', extra_where_clauses)

    with connection.cursor() as cursor:
        cursor.execute(sql, extra_arguments)
        rows = cursor.fetchall()

    return rows


def obtem_dados_relatorio_controle_sobras(form_data, user, bruto=False):
    extra_where_clauses = ""

    data_inicial = form_data['data_inicial'].strftime('%Y-%m-%d')
    data_final = form_data['data_final'].strftime('%Y-%m-%d')

    extra_arguments = [
        data_inicial, data_final,
        data_inicial, data_final,
        data_inicial, data_final
    ]

    if user.tipo_usuario == 'escola':
        extra_where_clauses = "AND cs.escola_id = %s"
        extra_arguments.append(user.vinculo_atual.instituicao.id)
    elif form_data['escola']:
        extra_where_clauses = "AND cs.escola_id = %s"
        extra_arguments.append(form_data['escola'].id)
    elif form_data['dre']:
        extra_where_clauses = "AND e.diretoria_regional_id = %s"
        extra_arguments.append(form_data['dre'].id)

    if bruto:
        sql = SQL_RELATORIO_CONTROLE_SOBRAS_BRUTO.replace('[EXTRA_WHERE_CLAUSES]', extra_where_clauses)
    else:
        sql = SQL_RELATORIO_CONTROLE_SOBRAS.replace('[EXTRA_WHERE_CLAUSES]', extra_where_clauses)

    with connection.cursor() as cursor:
        cursor.execute(sql, extra_arguments)
        rows = cursor.fetchall()

    return rows


def paginate_list(request, items_list, serializer, per_page=10):
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', per_page)

    paginator = Paginator(items_list, per_page)

    try:
        paginated_items = paginator.page(page)
    except EmptyPage:
        paginated_items = []

    data = {
        'count': paginator.count,
        'page_size': per_page,
        'results': [serializer(item) for item in paginated_items]
    }
    
    return data
