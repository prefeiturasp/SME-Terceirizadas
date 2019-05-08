from django.contrib import admin
from .models import FoodInclusion, FoodInclusionDescription, FoodInclusionReason, FoodInclusionStatus


admin.site.register(FoodInclusion)
admin.site.register(FoodInclusionDescription)
admin.site.register(FoodInclusionReason)
admin.site.register(FoodInclusionStatus)
