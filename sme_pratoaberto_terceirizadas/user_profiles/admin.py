from django.contrib import admin
from .models import NutritionistProfile, RegionalDirectorProfile


class NutritionistProfileAdmin(admin.ModelAdmin):
    list_display = ('regional_director',)


class RegionalDirectorProfileAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'description', 'sub_manager', 'alternate')
    search_fields = ('abbreviation',)


admin.site.register(NutritionistProfile, NutritionistProfileAdmin)
admin.site.register(RegionalDirectorProfile, RegionalDirectorProfileAdmin)
