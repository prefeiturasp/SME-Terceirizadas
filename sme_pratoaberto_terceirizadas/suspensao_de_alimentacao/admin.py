from django.contrib import admin
from .models import DiaRazaoSuspensaoDeAlimentacao, RazaoSuspensaoDeAlimentacao, SuspensaoDeAlimentacao, \
    DescricaoSuspensaoDeAlimentacao

admin.site.register(SuspensaoDeAlimentacao)
admin.site.register(DiaRazaoSuspensaoDeAlimentacao)
admin.site.register(RazaoSuspensaoDeAlimentacao)
admin.site.register(DescricaoSuspensaoDeAlimentacao)
