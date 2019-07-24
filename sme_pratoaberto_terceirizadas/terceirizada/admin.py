from django.contrib import admin
from .models import Lote, Terceirizada, Edital

admin.site.register(Edital)
admin.site.register(Lote)
admin.site.register(Terceirizada)
