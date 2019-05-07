import uuid

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from notifications.signals import notify
from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, TimestampAble
from sme_pratoaberto_terceirizadas.common_data.utils import str_to_date
from sme_pratoaberto_terceirizadas.food.models import MealType
from sme_pratoaberto_terceirizadas.food_inclusion.utils import get_object, object_exists
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
    priority = models.BooleanField(default=False)
    obs = models.TextField()

    def __str__(self):
        return '{name} - {id}'.format(name=self.status.name, id=self.id)

    class Meta:
        verbose_name = _("Food Inclusion")
        verbose_name_plural = _("Food Inclusions")

    def create_or_update(self, request_data, user):
        reason = request_data.get('reason')
        self._set_status(request_data)
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
            desc_uuid = description.get('uuid', None)
            food_inclusion_description = FoodInclusionDescription.objects.get(uuid=desc_uuid) \
                if desc_uuid else FoodInclusionDescription()
            food_inclusion_description.create_or_update(description, self)

    def _set_status(self, request_data):
        status = request_data.get('status', None)
        name = status if status else _('TO_VALIDATE')
        if not object_exists(FoodInclusionStatus, name=_('TO_VALIDATE')):
            default = FoodInclusionStatus(name=_('TO_VALIDATE'))
            default.save()
        self.status = get_object(FoodInclusionStatus, name=name)

    def _notification_aux(self, _type, validation_diff='creation'):
        notification_dict = {
            _('TO_VALIDATE'): {
                'recipient': User.objects.all(),
                'verb': _(validation_diff.capitalize()),
                'description': _('created') if validation_diff else _('edited')
            },
            _('TO_EDIT'): {
                'recipient': User.objects.all(),
                'verb': _('It needs edition'),
                'description': _('did not validated')
            },
            _('TO_APPROVE'): {
                'recipient': User.objects.all(),
                'verb': _('Validation'),
                'description': _('validated')
            },
            _('TO_VISUALIZE'): {
                'recipient': User.objects.all(),
                'verb': _('Approval'),
                'description': _('approved')
            },
            _('DENIED'): {
                'recipient': User.objects.all(),
                'verb': _('Denial'),
                'description': _('denied')
            },
            _('VISUALIZED'): {
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
    food_inclusion = models.ForeignKey(FoodInclusion, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{name} - {number_of_students}'.format(name=self.period.name,
                                                      number_of_students=str(self.number_of_students))

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
