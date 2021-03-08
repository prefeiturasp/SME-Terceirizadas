
def inativa_tipos_de_embabalagem(queryset):
    for tipo_embalagem in queryset.all():
        tipo_embalagem.ativo = False
        tipo_embalagem.save()
