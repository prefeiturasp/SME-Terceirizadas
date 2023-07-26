# Generated by Django 3.2.18 on 2023-07-25 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados_comuns', '0093_alter_logsolicitacoesusuario_status_evento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logsolicitacoesusuario',
            name='status_evento',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Solicitação Realizada'), (1, 'CODAE autorizou'), (2, 'Terceirizada tomou ciência'), (3, 'Terceirizada recusou'), (4, 'CODAE negou'), (5, 'CODAE pediu revisão'), (6, 'DRE revisou'), (7, 'DRE validou'), (8, 'DRE pediu revisão'), (9, 'DRE não validou'), (10, 'Escola revisou'), (13, 'Escola cancelou'), (14, 'CODAE negou cancelamento'), (15, 'DRE cancelou'), (11, 'Questionamento pela CODAE'), (12, 'Terceirizada respondeu questionamento'), (16, 'Escola solicitou cancelamento'), (17, 'CODAE autorizou cancelamento'), (18, 'CODAE negou cancelamento'), (19, 'Terceirizada tomou ciência do cancelamento'), (20, 'Cancelada por atingir data de término'), (21, 'Pendente homologação da CODAE'), (22, 'CODAE homologou'), (23, 'CODAE não homologou'), (24, 'CODAE pediu análise sensorial'), (25, 'CODAE cancelou análise sensorial'), (26, 'Terceirizada cancelou homologação'), (31, 'Homologação inativa'), (32, 'Terceirizada cancelou solicitação de homologação de produto'), (27, 'CODAE suspendeu o produto'), (28, 'Escola/Nutricionista reclamou do produto'), (29, 'CODAE pediu análise da reclamação'), (30, 'CODAE autorizou reclamação'), (39, 'CODAE recusou reclamação'), (40, 'CODAE questionou terceirizada sobre reclamação'), (35, 'CODAE questionou U.E. sobre reclamação'), (41, 'CODAE respondeu ao reclamante da reclamação'), (38, 'CODAE questionou nutrisupervisor sobre reclamação'), (33, 'Terceirizada respondeu a reclamação'), (36, 'U.E. respondeu a reclamação'), (37, 'Nutrisupervisor respondeu a reclamação'), (34, 'Terceirizada respondeu a análise'), (43, 'Papa enviou a requisição'), (44, 'Dilog Enviou a requisição'), (45, 'Distribuidor confirmou requisição'), (46, 'Distribuidor pede alteração da requisição'), (47, 'Papa cancelou a requisição'), (48, 'Papa aguarda confirmação do cancelamento da solicitação'), (49, 'Distribuidor confirmou cancelamento e Papa cancelou a requisição'), (50, 'Dilog Aceita Alteração'), (51, 'Dilog Nega Alteração'), (52, 'Cancelamento por alteração de unidade educacional'), (53, 'Cancelamento para aluno não matriculado na rede municipal'), (54, 'Em aberto para preenchimento pela UE'), (55, 'Enviado pela UE'), (64, 'Correção solicitada'), (65, 'Corrigido para DRE'), (66, 'Aprovado pela DRE'), (67, 'Aprovado pela CODAE'), (56, 'Cronograma Criado'), (57, 'Assinado e Enviado ao Fornecedor'), (58, 'Assinado Fornecedor'), (59, 'Solicitada Alteração'), (60, 'Suspenso em alguns editais'), (61, 'Ativo em alguns editais'), (62, 'Assinado Cronograma'), (63, 'CODAE Atualizou o protocolo'), (68, 'Assinado DINUTRE'), (69, 'Assinado CODAE'), (70, 'Vínculo do Edital ao Produto'), (71, 'Cronograma Ciente'), (72, 'Aprovado DINUTRE'), (73, 'Reprovado DINUTRE'), (74, 'Aprovado DILOG'), (75, 'Reprovado DILOG'), (76, 'CODAE cancelou solicitação de correção'), (77, 'Terceirizada cancelou solicitação de correção'), (78, 'Em Análise'), (79, 'Notificação criada'), (80, 'Notificação enviada para o fiscal'), (81, 'Correção solicitada pela CODAE'), (82, 'Corrigido para CODAE')]),
        ),
    ]
