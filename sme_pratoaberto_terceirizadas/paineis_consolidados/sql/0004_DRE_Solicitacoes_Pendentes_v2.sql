DROP VIEW DRE_solicitacoes_pendentes;

CREATE OR REPLACE VIEW DRE_solicitacoes_pendentes AS
-- Essa view consolida todas as solicitacoes pendentes para as DREs

-- Alteracoes de cardapio
SELECT cardapio.id,
       cardapio.uuid,
	   cardapio.data_inicial AS data_doc,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS data_log,
       'ALT_CARDAPIO' AS tipo_doc
FROM cardapio_alteracaocardapio AS cardapio,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs
WHERE escola.id = cardapio.escola_id
  AND lote.id = escola.lote_id
  AND cardapio.uuid = logs.uuid_original
  AND logs.status_evento = 0
  AND cardapio.status = 'DRE_A_VALIDAR'
GROUP BY cardapio.id,
         lote.nome,
         escola.diretoria_regional_id
UNION

-- Inclusoes de alimentacao
SELECT inc_alimentacao.id,
       inc_alimentacao.uuid,
	   min(inc_alimentacao_item.data) AS data_doc,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS data_log,
       'INC_ALIMENTA' AS tipo_doc
FROM inclusao_alimentacao_grupoinclusaoalimentacaonormal AS inc_alimentacao,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs,
	 inclusao_alimentacao_inclusaoalimentacaonormal as inc_alimentacao_item
WHERE escola.id = inc_alimentacao.escola_id
  AND lote.id = escola.lote_id
  AND inc_alimentacao.uuid = logs.uuid_original
  AND logs.status_evento = 0
  AND inc_alimentacao.status = 'DRE_A_VALIDAR'
  AND inc_alimentacao_item.grupo_inclusao_id = inc_alimentacao.id
GROUP BY inc_alimentacao.id,
         lote.nome,
         escola.diretoria_regional_id

UNION

-- Inversoes de cardapio
SELECT inv_cardapio.id,
    inv_cardapio.uuid,
	CASE WHEN cardapio_de.data <= cardapio_para.data THEN cardapio_de.data ELSE cardapio_para.data END AS data_doc,
    lote.nome AS lote,
    escola.diretoria_regional_id,
    max(logs.criado_em) AS data_log,
    'INV_CARDAPIO'::text AS tipo_doc
  FROM cardapio_inversaocardapio inv_cardapio,
    escola_escola escola,
    escola_lote lote,
    dados_comuns_logsolicitacoesusuario logs,
	cardapio_cardapio as cardapio_de,
	cardapio_cardapio as cardapio_para

  WHERE escola.id = inv_cardapio.escola_id
  	AND lote.id = escola.lote_id
	AND inv_cardapio.uuid = logs.uuid_original
	AND logs.status_evento = 0
	AND inv_cardapio.status::text = 'DRE_A_VALIDAR'::text
	AND cardapio_de.id = inv_cardapio.cardapio_de_id
	AND cardapio_para.id = inv_cardapio.cardapio_para_id

  GROUP BY inv_cardapio.id, lote.nome, escola.diretoria_regional_id, cardapio_de.data, cardapio_para.data

UNION

-- Kit Lanches Solicitacoes Avulsas
SELECT kit_lanche.id,
       kit_lanche.uuid,
	   min(kit_lanche_item.data) as data_doc,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS data_log,
       'KIT_LANCHE_AVULSA' AS tipo_doc
FROM kit_lanche_solicitacaokitlancheavulsa AS kit_lanche,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs,
	 kit_lanche_solicitacaokitlanche as kit_lanche_item
WHERE escola.id = kit_lanche.escola_id
  AND lote.id = escola.lote_id
  AND kit_lanche.uuid = logs.uuid_original
  AND logs.status_evento = 0
  AND kit_lanche.status = 'DRE_A_VALIDAR'
  AND kit_lanche_item.id = kit_lanche.id
GROUP BY kit_lanche.id,
         lote.nome,
         escola.diretoria_regional_id
UNION

-- Suspensoes de Alimentacao
SELECT susp_alimentacao.id,
       susp_alimentacao.uuid,
	   min(susp_alimentacao_item.data) AS data_doc,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS data_log,
       'SUSP_ALIMENTACAO' AS tipo_doc
FROM cardapio_gruposuspensaoalimentacao AS susp_alimentacao,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs,
	 cardapio_suspensaoalimentacao as susp_alimentacao_item
WHERE escola.id = susp_alimentacao.escola_id
  AND lote.id = escola.lote_id
  AND susp_alimentacao.uuid = logs.uuid_original
  AND susp_alimentacao_item.grupo_suspensao_id = susp_alimentacao.id
  AND logs.status_evento = 0
  AND susp_alimentacao.status = 'DRE_A_VALIDAR'
GROUP BY susp_alimentacao.id,
         lote.nome,
         escola.diretoria_regional_id

ORDER BY data_log DESC
