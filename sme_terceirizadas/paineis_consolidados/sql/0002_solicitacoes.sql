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
  union

  SELECT inc_aliment_normal.id,
         inc_aliment_normal.uuid,
         min(inc_alimentacao_item.data) AS data_evento,
         lote.nome                      as lote_nome,
         dre.nome                       as dre_nome,
         escola.nome                    as escola_nome,
         'INC_ALIMENTA'                 AS tipo_doc,
         'Inclusão de Alimentação'      AS desc_doc,
         inc_aliment_normal.status      as status_atual,
         logs.criado_em                 as data_log,
         logs.status_evento
  FROM inclusao_alimentacao_grupoinclusaoalimentacaonormal AS inc_aliment_normal
         left join dados_comuns_logsolicitacoesusuario as logs on logs.uuid_original = inc_aliment_normal.uuid
         left join escola_diretoriaregional as dre on dre.id = inc_aliment_normal.rastro_dre_id
         left join escola_lote as lote on lote.id = inc_aliment_normal.rastro_lote_id
         left join escola_escola as escola on escola.id = inc_aliment_normal.rastro_escola_id
         left join terceirizada_terceirizada as terceirizada
                   on terceirizada.id = inc_aliment_normal.rastro_terceirizada_id
         left join inclusao_alimentacao_inclusaoalimentacaonormal AS inc_alimentacao_item
                   on inc_alimentacao_item.grupo_inclusao_id = inc_aliment_normal.id

  group by inc_aliment_normal.id, lote.nome, dre.nome, escola.nome, logs.criado_em, logs.status_evento
  union
  SELECT inc_aliment_continua.id,
         inc_aliment_continua.uuid,
         inc_aliment_continua.data_inicial  AS data_evento,
         lote.nome                          as lote_nome,
         dre.nome                           as dre_nome,
         escola.nome                        as escola_nome,
         'INC_ALIMENTA_CONTINUA'            AS tipo_doc,
         'Inclusão de Alimentação Contínua' AS desc_doc,
         inc_aliment_continua.status        as status_atual,
         logs.criado_em                     as data_log,
         logs.status_evento
  FROM inclusao_alimentacao_inclusaoalimentacaocontinua AS inc_aliment_continua
         left join dados_comuns_logsolicitacoesusuario as logs on logs.uuid_original = inc_aliment_continua.uuid
         left join escola_diretoriaregional as dre on dre.id = inc_aliment_continua.rastro_dre_id
         left join escola_lote as lote on lote.id = inc_aliment_continua.rastro_lote_id
         left join escola_escola as escola on escola.id = inc_aliment_continua.rastro_escola_id
         left join terceirizada_terceirizada as terceirizada
                   on terceirizada.id = inc_aliment_continua.rastro_terceirizada_id

  union
  SELECT kit_lanche_avulso.id,
         kit_lanche_avulso.uuid,
         min(kit_lanche_base.data) AS data_evento,
         lote.nome                 as lote_nome,
         dre.nome                  as dre_nome,
         escola.nome               as escola_nome,
         'KIT_LANCHE_AVULSA'       AS tipo_doc,
         'Kit Lanche Passeio'      AS desc_doc,
         kit_lanche_avulso.status  as status_atual,
         logs.criado_em            as data_log,
         logs.status_evento
  FROM kit_lanche_solicitacaokitlancheavulsa AS kit_lanche_avulso
         left join dados_comuns_logsolicitacoesusuario as logs on logs.uuid_original = kit_lanche_avulso.uuid
         left join escola_diretoriaregional as dre on dre.id = kit_lanche_avulso.rastro_dre_id
         left join escola_lote as lote on lote.id = kit_lanche_avulso.rastro_lote_id
         left join escola_escola as escola on escola.id = kit_lanche_avulso.rastro_escola_id
         left join terceirizada_terceirizada as terceirizada
                   on terceirizada.id = kit_lanche_avulso.rastro_terceirizada_id
         left join kit_lanche_solicitacaokitlanche AS kit_lanche_base
                   on kit_lanche_base.id = kit_lanche_avulso.solicitacao_kit_lanche_id
  group by kit_lanche_avulso.id, lote.nome, escola.nome, dre.nome, logs.criado_em, logs.status_evento

  union
  SELECT grupo_suspensao.id,
         grupo_suspensao.uuid,
         min(susp_alimentacao_item.data) AS data_evento,
         lote.nome                       as lote_nome,
         dre.nome                        as dre_nome,
         escola.nome                     as escola_nome,
         'SUSP_ALIMENTACAO'              AS tipo_doc,
         'Suspensão de Alimentação'      AS desc_doc,
         grupo_suspensao.status          as status_atual,
         logs.criado_em                  as data_log,
         logs.status_evento
  FROM cardapio_gruposuspensaoalimentacao AS grupo_suspensao
         left join dados_comuns_logsolicitacoesusuario as logs on logs.uuid_original = grupo_suspensao.uuid
         left join escola_diretoriaregional as dre on dre.id = grupo_suspensao.rastro_dre_id
         left join escola_lote as lote on lote.id = grupo_suspensao.rastro_lote_id
         left join escola_escola as escola on escola.id = grupo_suspensao.rastro_escola_id
         left join terceirizada_terceirizada as terceirizada
                   on terceirizada.id = grupo_suspensao.rastro_terceirizada_id
         left join cardapio_suspensaoalimentacao AS susp_alimentacao_item
                   on susp_alimentacao_item.grupo_suspensao_id = grupo_suspensao.id
  group by grupo_suspensao.id, lote.nome, escola.nome, dre.nome, logs.criado_em, logs.status_evento

