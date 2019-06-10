import uuid

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.translation import ugettext as _
from notifications.signals import notify

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, TimestampAble, Activable
from sme_pratoaberto_terceirizadas.common_data.utils import str_to_date, get_working_days_after
from sme_pratoaberto_terceirizadas.food.models import MealType
from sme_pratoaberto_terceirizadas.food_inclusion.utils import get_object
from sme_pratoaberto_terceirizadas.school.models import SchoolPeriod
from sme_pratoaberto_terceirizadas.users.models import User


class FoodInclusionStatus(Describable):
    """Status da Inclusão de Alimentação"""

    SAVED = "SALVO"
    TO_VALIDATE = _('TO_VALIDATE')
    TO_APPROVE = _('TO_APPROVE')
    TO_EDIT = _('TO_EDIT')
    TO_VISUALIZE = _('TO_VISUALIZE')
    DENIED_BY_CODAE = _('DENIED_BY_CODAE')
    DENIED_BY_COMPANY = _('DENIED_BY_COMPANY')
    VISUALIZED = _('VISUALIZED')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")


class FoodInclusionReason(Describable, Activable):
    """Motivo para Inclusão de Alimentação"""

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Reason")
        verbose_name_plural = _("Reasons")


class FoodInclusion(TimestampAble):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.ForeignKey(FoodInclusionStatus, on_delete=models.DO_NOTHING)
    denied_by_company = models.BooleanField(default=False)
    denial_reason = models.TextField(blank=True, null=True)
    obs = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{name} - {id}'.format(name=self.status.name, id=self.id)

    class Meta:
        verbose_name = _("Food Inclusion")
        verbose_name_plural = _("Food Inclusions")

    def create_or_update(self, request_data, user):
        self._set_status(request_data)
        self.created_by = user
        self.obs = request_data.get('obs', None)
        self.save()
        self._create_or_update_day_reasons(request_data)
        self._create_or_update_descriptions(request_data)

    def _create_or_update_day_reasons(self, request_data):
        day_reasons = request_data.get('day_reasons')
        for day_reason in day_reasons:
            day_reason_uuid = day_reason.get('uuid', None)
            food_inclusion_day_reason = FoodInclusionDayReason.objects.get(uuid=day_reason_uuid) \
                if day_reason_uuid else FoodInclusionDayReason()
            food_inclusion_day_reason.create_or_update(day_reason, self)

    def _create_or_update_descriptions(self, request_data):
        descriptions = [request_data.get('description_first_period', None),
                        request_data.get('description_second_period', None),
                        request_data.get('description_third_period', None),
                        request_data.get('description_fourth_period', None),
                        request_data.get('description_integrate', None)]
        for description in descriptions:
            if description:
                desc_uuid = description.get('uuid', None)
                food_inclusion_description = FoodInclusionDescription.objects.get(uuid=desc_uuid) \
                    if desc_uuid else FoodInclusionDescription()
                food_inclusion_description.create_or_update(description, self)

    def _set_status(self, request_data):
        status = request_data.get('status', None)
        name = status if status else FoodInclusionStatus.TO_VALIDATE
        self.status = get_object(FoodInclusionStatus, name=name)

    def _notification_aux(self, _type, validation_diff='creation'):
        notification_dict = {
            FoodInclusionStatus.TO_VALIDATE: {
                'recipient': User.objects.all(),
                'verb': _(validation_diff.capitalize()),
                'description': _('created') if validation_diff else _('edited')
            },
            FoodInclusionStatus.TO_EDIT: {
                'recipient': User.objects.all(),
                'verb': _('It needs edition'),
                'description': _('did not validated')
            },
            FoodInclusionStatus.TO_APPROVE: {
                'recipient': User.objects.all(),
                'verb': _('Validation'),
                'description': _('validated')
            },
            FoodInclusionStatus.TO_VISUALIZE: {
                'recipient': User.objects.all(),
                'verb': _('Approval'),
                'description': _('approved')
            },
            FoodInclusionStatus.DENIED_BY_CODAE: {
                'recipient': User.objects.all(),
                'verb': _('Denial by CODAE'),
                'description': _('denied by CODAE')
            },
            FoodInclusionStatus.DENIED_BY_COMPANY: {
                'recipient': User.objects.all(),
                'verb': _('Denial by Company'),
                'description': _('denied by company')
            },
            FoodInclusionStatus.VISUALIZED: {
                'recipient': User.objects.all(),
                'verb': _('Visualization'),
                'description': _('visualized')
            },
        }
        return notification_dict[self.status.name][_type]

    def send_notification(self, actor, validation_diff='creation'):
        notify.send(
            sender=actor,
            recipient=self._notification_aux('recipient', validation_diff),
            verb=_('Food Inclusion - ') + self._notification_aux('verb', validation_diff),
            action_object=self,
            description=_('The user ') + actor.name + self._notification_aux('description', validation_diff) +
                        _(' a food inclusion.'))


class FoodInclusionDescription(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    period = models.ForeignKey(SchoolPeriod, on_delete=models.DO_NOTHING)
    meal_type = models.ManyToManyField(MealType)
    number_of_students = models.IntegerField()
    food_inclusion = models.ForeignKey(FoodInclusion, on_delete=models.CASCADE)

    def __str__(self):
        return '{name} - {number_of_students}'.format(name=self.period.name,
                                                      number_of_students=str(self.number_of_students))

    class Meta:
        verbose_name = _("Food Inclusion description")
        verbose_name_plural = _("Food Inclusion descriptions")

    def create_or_update(self, request_data, food_inclusion):
        school_period = request_data.get('value')
        meal_types = request_data.get('select') if isinstance(request_data.get('select'), list) else [
            request_data.get('select')]
        self.number_of_students = request_data.get('number')
        self.food_inclusion = food_inclusion
        self.period = get_object(SchoolPeriod, value=school_period)
        self.save()
        for meal_type in meal_types:
            self.meal_type.add(get_object(MealType, name=meal_type))
        self.save()


class FoodInclusionDayReason(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    food_inclusion = models.ForeignKey(FoodInclusion, on_delete=models.CASCADE)
    reason = models.ForeignKey(FoodInclusionReason, on_delete=models.DO_NOTHING)
    which_reason = models.TextField(blank=True, null=True)
    priority = models.BooleanField(default=False)
    date = models.DateField(blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    weekdays = models.CharField(blank=True, null=True, max_length=14,
                                validators=[validate_comma_separated_integer_list])

    def create_or_update(self, request_data, food_inclusion):
        date = request_data.get('date', None)
        reason = request_data.get('reason')
        self.reason = FoodInclusionReason.objects.get(name=reason)
        self.which_reason = request_data.get('which_reason', None)
        self.food_inclusion = food_inclusion
        if date:
            self.date = str_to_date(date)
            self.priority = get_working_days_after(days=2) <= self.date <= get_working_days_after(days=5)
            self.date_from = None
            self.date_to = None
            self.weekdays = None
        else:
            self.date = None
            self.date_from = str_to_date(request_data.get('date_from'))
            self.date_to = str_to_date(request_data.get('date_to'))
            self.weekdays = ",".join(request_data.get('weekdays', None))
        self.save()
