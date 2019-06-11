from django.contrib import admin
from .models import DiaRazaoSuspensaoDeAlimentacao, RazaoSuspensaoDeAlimentacao, SuspensaoDeAlimentacao, \
    DescricaoSuspensaoDeAlimentacao, StatusSuspensaoDeAlimentacao

admin.site.register(SuspensaoDeAlimentacao)
admin.site.register(DiaRazaoSuspensaoDeAlimentacao)
admin.site.register(RazaoSuspensaoDeAlimentacao)
admin.site.register(DescricaoSuspensaoDeAlimentacao)
admin.site.register(StatusSuspensaoDeAlimentacao)
