CREATE VIEW DRE_solicitacoes_autorizadas AS
-- TODO Incluir esse script no migrations do Django
-- Essa view consolida todas as solicitacoes autorizadas pelas DREs

-- Alteracoes de cardapio
select cardapio.id, cardapio.uuid, lote.nome AS lote, escola.diretoria_regional_id, max(logs.criado_em) as data, 'ALT_CARDAPIO' as tipo_doc
from cardapio_alteracaocardapio AS cardapio, escola_escola AS escola, escola_lote AS lote, dados_comuns_logsolicitacoesusuario AS logs
where escola.id = cardapio.escola_id and lote.id = escola.lote_id and cardapio.uuid = logs.uuid_original and logs.status_evento = 7
group by cardapio.id, lote.nome, escola.diretoria_regional_id

union

-- Inclusoes de alimentacao
select inc_alimentacao.id, inc_alimentacao.uuid, lote.nome AS lote, escola.diretoria_regional_id, max(logs.criado_em) as data, 'INC_ALIMENTA' as tipo_doc
from inclusao_alimentacao_grupoinclusaoalimentacaonormal as inc_alimentacao, escola_escola AS escola, escola_lote AS lote, dados_comuns_logsolicitacoesusuario AS logs
where escola.id = inc_alimentacao.escola_id and lote.id = escola.lote_id and inc_alimentacao.uuid = logs.uuid_original and logs.status_evento = 7
group by inc_alimentacao.id, lote.nome, escola.diretoria_regional_id

union

-- Inversoes de cardapio
select inv_cardapio.id, inv_cardapio.uuid, lote.nome AS lote, escola.diretoria_regional_id, max(logs.criado_em) as data, 'INV_CARDAPIO' as tipo_doc
from cardapio_inversaocardapio as inv_cardapio, escola_escola AS escola, escola_lote AS lote, dados_comuns_logsolicitacoesusuario AS logs
where escola.id = inv_cardapio.escola_id and lote.id = escola.lote_id and inv_cardapio.uuid = logs.uuid_original and logs.status_evento = 7
group by inv_cardapio.id, lote.nome, escola.diretoria_regional_id

union

-- Kit Lanches Solicitacoes Avulsas
select kit_lanche.id, kit_lanche.uuid, lote.nome AS lote, escola.diretoria_regional_id, max(logs.criado_em) as data, 'KIT_LANCHE_AVULSA' as tipo_doc
from kit_lanche_solicitacaokitlancheavulsa as kit_lanche, escola_escola AS escola, escola_lote AS lote, dados_comuns_logsolicitacoesusuario AS logs
where escola.id = kit_lanche.escola_id and lote.id = escola.lote_id and kit_lanche.uuid = logs.uuid_original and logs.status_evento = 7
group by kit_lanche.id, lote.nome, escola.diretoria_regional_id

union

-- Suspensoes de Alimentacao
select susp_alimentacao.id, susp_alimentacao.uuid, lote.nome AS lote, escola.diretoria_regional_id, max(logs.criado_em) as data, 'SUSP_ALIMENTACAO' as tipo_doc
from cardapio_gruposuspensaoalimentacao as susp_alimentacao, escola_escola AS escola, escola_lote AS lote, dados_comuns_logsolicitacoesusuario AS logs
where escola.id = susp_alimentacao.escola_id and lote.id = escola.lote_id and susp_alimentacao.uuid = logs.uuid_original and logs.status_evento = 7
group by susp_alimentacao.id, lote.nome, escola.diretoria_regional_id

order by data desc
