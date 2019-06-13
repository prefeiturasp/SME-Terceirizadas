from django.contrib import admin
from .models import MealKit, OrderMealKit, SolicitacaoUnificada, SolicitacaoUnificadaFormulario, \
    SolicitacaoUnificadaMultiploEscola, RazaoSolicitacaoUnificada, StatusSolicitacaoUnificada


@admin.register(MealKit)
class MealKitAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    ordering = ('name', 'is_active')


@admin.register(OrderMealKit)
class OrderMealKitAdmin(admin.ModelAdmin):
    list_display = ['location', 'students_quantity', 'order_date', 'status']


admin.site.register(RazaoSolicitacaoUnificada)
admin.site.register(SolicitacaoUnificada)
admin.site.register(SolicitacaoUnificadaMultiploEscola)
admin.site.register(SolicitacaoUnificadaFormulario)
admin.site.register(StatusSolicitacaoUnificada)
