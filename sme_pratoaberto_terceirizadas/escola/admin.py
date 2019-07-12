from django.contrib import admin

from .models import (TipoGestao, TipoUnidadeEscolar, FaixaIdadeEscolar,
                     DiretoriaRegional, PeriodoEscolar, Escola)

admin.site.register(Escola)
admin.site.register(DiretoriaRegional)
admin.site.register(PeriodoEscolar)
admin.site.register(TipoGestao)
admin.site.register(TipoUnidadeEscolar)
admin.site.register(FaixaIdadeEscolar)
