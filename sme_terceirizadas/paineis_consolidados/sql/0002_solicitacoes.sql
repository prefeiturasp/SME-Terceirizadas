DROP VIEW IF EXISTS solicitacoes_consolidadas;

CREATE OR REPLACE VIEW solicitacoes_consolidadas AS
  SELECT cardapio.id,
         cardapio.uuid,
         cardapio.data_inicial   AS data_evento,
         lote.nome               as lote_nome,
         dre.nome                as dre_nome,
         escola.nome             as escola_nome,
         'ALT_CARDAPIO'          AS tipo_doc,
         'Alteração de Cardápio' AS desc_doc,
         cardapio.status         as status_atual,
         logs.criado_em          as data_log,
         logs.status_evento
  FROM cardapio_alteracaocardapio AS cardapio
         left join dados_comuns_logsolicitacoesusuario as logs on logs.uuid_original = cardapio.uuid
         left join escola_diretoriaregional as dre on dre.id = cardapio.rastro_dre_id
         left join escola_lote as lote on lote.id = cardapio.rastro_lote_id
         left join escola_escola as escola on escola.id = cardapio.rastro_escola_id
         left join terceirizada_terceirizada as terceirizada on terceirizada.id = cardapio.rastro_terceirizada_id
  union

  SELECT inversao_cardapio.id,
         inversao_cardapio.uuid,
         CASE
           WHEN cardapio_de.data <= cardapio_para.data THEN cardapio_de.data
           ELSE cardapio_para.data END AS data_evento,
         lote.nome                     as lote_nome,
         dre.nome                      as dre_nome,
         escola.nome                   as escola_nome,
         'INV_CARDAPIO'                AS tipo_doc,
         'Inversão de dia de Cardápio' AS desc_doc,
         inversao_cardapio.status      as status_atual,
         logs.criado_em                as data_log,
         logs.status_evento
  FROM cardapio_inversaocardapio AS inversao_cardapio
         left join dados_comuns_logsolicitacoesusuario as logs on logs.uuid_original = inversao_cardapio.uuid
         left join escola_diretoriaregional as dre on dre.id = inversao_cardapio.rastro_dre_id
         left join escola_lote as lote on lote.id = inversao_cardapio.rastro_lote_id
         left join escola_escola as escola on escola.id = inversao_cardapio.rastro_escola_id
         left join terceirizada_terceirizada as terceirizada
                   on terceirizada.id = inversao_cardapio.rastro_terceirizada_id
         left join cardapio_cardapio as cardapio_de on cardapio_de.id = inversao_cardapio.cardapio_de_id
         left join cardapio_cardapio as cardapio_para on cardapio_para.id = inversao_cardapio.cardapio_para_id

