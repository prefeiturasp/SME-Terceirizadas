CREATE OR REPLACE VIEW CODAE_solicitacoes_pendentes AS
-- Essa view consolida todas as solicitacoes pendentes para a CODAE
-- Alteracoes de cardapio

SELECT cardapio.id,
       cardapio.uuid,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS DATA,
       'ALT_CARDAPIO' AS tipo_doc
FROM cardapio_alteracaocardapio AS cardapio,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs
WHERE escola.id = cardapio.escola_id
  AND lote.id = escola.lote_id
  AND cardapio.uuid = logs.uuid_original
  AND logs.status_evento = 1
  AND cardapio.status = 'CODAE_APROVADO'
GROUP BY cardapio.id,
         lote.nome,
         escola.diretoria_regional_id
UNION
-- Inclusoes de alimentacao

SELECT inc_alimentacao.id,
       inc_alimentacao.uuid,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS DATA,
       'INC_ALIMENTA' AS tipo_doc
FROM inclusao_alimentacao_grupoinclusaoalimentacaonormal AS inc_alimentacao,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs
WHERE escola.id = inc_alimentacao.escola_id
  AND lote.id = escola.lote_id
  AND inc_alimentacao.uuid = logs.uuid_original
  AND logs.status_evento = 1
  AND inc_alimentacao.status = 'CODAE_APROVADO'
GROUP BY inc_alimentacao.id,
         lote.nome,
         escola.diretoria_regional_id
UNION
-- Inversoes de cardapio

SELECT inv_cardapio.id,
       inv_cardapio.uuid,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS DATA,
       'INV_CARDAPIO' AS tipo_doc
FROM cardapio_inversaocardapio AS inv_cardapio,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs
WHERE escola.id = inv_cardapio.escola_id
  AND lote.id = escola.lote_id
  AND inv_cardapio.uuid = logs.uuid_original
  AND logs.status_evento = 1
  AND inv_cardapio.status = 'CODAE_APROVADO'
GROUP BY inv_cardapio.id,
         lote.nome,
         escola.diretoria_regional_id
UNION
-- Kit Lanches Solicitacoes Avulsas

SELECT kit_lanche.id,
       kit_lanche.uuid,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS DATA,
       'KIT_LANCHE_AVULSA' AS tipo_doc
FROM kit_lanche_solicitacaokitlancheavulsa AS kit_lanche,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs
WHERE escola.id = kit_lanche.escola_id
  AND lote.id = escola.lote_id
  AND kit_lanche.uuid = logs.uuid_original
  AND logs.status_evento = 1
  AND kit_lanche.status = 'CODAE_APROVADO'
GROUP BY kit_lanche.id,
         lote.nome,
         escola.diretoria_regional_id
UNION
-- Suspensoes de Alimentacao

SELECT susp_alimentacao.id,
       susp_alimentacao.uuid,
       lote.nome AS lote,
       escola.diretoria_regional_id,
       max(logs.criado_em) AS DATA,
       'SUSP_ALIMENTACAO' AS tipo_doc
FROM cardapio_gruposuspensaoalimentacao AS susp_alimentacao,
     escola_escola AS escola,
     escola_lote AS lote,
     dados_comuns_logsolicitacoesusuario AS logs
WHERE escola.id = susp_alimentacao.escola_id
  AND lote.id = escola.lote_id
  AND susp_alimentacao.uuid = logs.uuid_original
  AND logs.status_evento = 1
  AND susp_alimentacao.status = 'CODAE_APROVADO'
GROUP BY susp_alimentacao.id,
         lote.nome,
         escola.diretoria_regional_id
ORDER BY DATA DESC
