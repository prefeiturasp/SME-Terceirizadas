from django.contrib import admin

from .models import Cronograma, EtapasDoCronograma, ProgramacaoDoRecebimentoDoCronograma

admin.site.register(Cronograma)
admin.site.register(EtapasDoCronograma)
admin.site.register(ProgramacaoDoRecebimentoDoCronograma)
