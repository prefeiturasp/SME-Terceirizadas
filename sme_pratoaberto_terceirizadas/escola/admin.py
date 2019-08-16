from django.contrib import admin

from .models import (TipoGestao, TipoUnidadeEscolar, FaixaIdadeEscolar, Subprefeitura,
                     DiretoriaRegional, PeriodoEscolar, Escola, Lote, Codae)

admin.site.register(DiretoriaRegional)
admin.site.register(Escola)
admin.site.register(FaixaIdadeEscolar)
admin.site.register(Lote)
admin.site.register(PeriodoEscolar)
admin.site.register(Subprefeitura)
admin.site.register(TipoGestao)
admin.site.register(TipoUnidadeEscolar)
admin.site.register(Codae)
