import uuid

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, TimestampAble
from sme_pratoaberto_terceirizadas.common_data.utils import str_to_date
from sme_pratoaberto_terceirizadas.food.models import MealType
from sme_pratoaberto_terceirizadas.food_inclusion.utils import get_object, get_status_or_default, object_exists
from sme_pratoaberto_terceirizadas.school.models import SchoolPeriod
from sme_pratoaberto_terceirizadas.users.models import User


class FoodInclusionStatus(Describable):
    """Status da Inclusão de Alimentação"""

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")


class FoodInclusionReason(Describable):
    """Motivo para Inclusão de Alimentação"""

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Reason")
        verbose_name_plural = _("Reasons")


class FoodInclusion(TimestampAble):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reason = models.ForeignKey(FoodInclusionReason, on_delete=models.DO_NOTHING)
    date = models.DateField(blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    weekdays = models.CharField(blank=True, null=True, max_length=14,
                                validators=[validate_comma_separated_integer_list])
    status = models.ForeignKey(FoodInclusionStatus, on_delete=models.DO_NOTHING)
    obs = models.TextField()

    def __str__(self):
        return self.status.name + ' - ' + str(self.id)

    class Meta:
        verbose_name = _("Food Inclusion")
        verbose_name_plural = _("Food Inclusions")

    def create_or_update(self, request_data, user):
        reason = request_data.get('reason')
        self.status = get_status_or_default(request_data)
        self.created_by = user
        self.reason = get_object(FoodInclusionReason, name=reason)
        self._assign_date_block(request_data)
        self.obs = request_data.get('obs', None)
        self.save()
        self._create_or_update_descriptions(request_data)

    def _assign_date_block(self, request_data):
        if 'date' in request_data.keys():
            self.date = str_to_date(request_data.get('date'), '%Y%m%d')
            self.date_from = None
            self.date_to = None
            self.weekdays = None
        else:
            self.date = None
            self.date_from = str_to_date(request_data.get('date_from'), '%Y%m%d')
            self.date_to = str_to_date(request_data.get('date_to'), '%Y%m%d')
            self.weekdays = request_data.get('weekdays', None)

    def _create_or_update_descriptions(self, request_data):
        descriptions = request_data.get('descriptions')
        for description in descriptions:
            uuid_description = description.get('uuid', None)
            food_inclusion_description = FoodInclusionDescription.objects.get(uuid=uuid_description) \
                if uuid_description else FoodInclusionDescription()
            food_inclusion_description.create_or_update(description, self)


class FoodInclusionDescription(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    period = models.ForeignKey(SchoolPeriod, on_delete=models.DO_NOTHING)
    meal_type = models.ManyToManyField(MealType)
    number_of_students = models.IntegerField()
    food_inclusion = models.ForeignKey(FoodInclusion, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.period.name + ' - ' + str(self.number_of_students)

    class Meta:
        verbose_name = _("Food Inclusion")
        verbose_name_plural = _("Food Inclusions")

    def create_or_update(self, request_data, food_inclusion):
        school_period = request_data.get('school_period')
        meal_type = request_data.get('meal_type')
        self.number_of_students = request_data.get('number_of_students')
        self.food_inclusion = food_inclusion
        self.period = get_object(SchoolPeriod, name=school_period)
        self.save()
        self.meal_type.add(get_object(MealType, name=meal_type))
        self.save()

@receiver(pre_save, sender=FoodInclusion)
def food_inclusion_pre_save(sender, instance, *args, **kwargs):
    if instance.weekdays:
        validate_comma_separated_integer_list(instance.weekdays)
