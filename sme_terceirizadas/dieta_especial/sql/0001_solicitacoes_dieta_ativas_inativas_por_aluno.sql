CREATE VIEW dietas_ativas_inativas_por_aluno AS
SELECT
	codigo_eol,
	nome nome_aluno,
	sum(case when ativo then 1 else 0 end) ativas,
	sum(case when ativo then 0 else 1 end) inativas
  FROM dieta_especial_solicitacaodietaespecial, escola_aluno
  WHERE dieta_especial_solicitacaodietaespecial.aluno_id = escola_aluno.id
  GROUP BY codigo_eol, nome_aluno
  ORDER BY nome_aluno;
