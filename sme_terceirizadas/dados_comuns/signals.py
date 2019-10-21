def salva_rastro_inversao_alteracao_suspensao(sender, instance, created, **kwargs):
    if created:
        instance.rastro_escola = instance.escola
        instance.rastro_dre = instance.escola.diretoria_regional
        instance.rastro_lote = instance.escola.lote
        instance.rastro_terceirizada = instance.escola.lote.terceirizada
        instance.save()
