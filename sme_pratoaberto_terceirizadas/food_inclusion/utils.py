import datetime

from django.utils.translation import ugettext_lazy as _
from notifications.signals import notify
from ..food.models import MealType
from ..food_inclusion import models
from ..school.models import SchoolPeriod


def validate_date_format(date_text, errors_list):
    try:
        datetime.datetime.strptime(date_text, '%Y%m%d')
    except ValueError:
        errors_list.append(_('incorrect data format, should be YYYYMMDD'))


def validate_weekdays(weekdays, errors_list):
    try:
        for weekday in weekdays:
            if weekday not in ['0', '1', '2', '3', '4', '5', '6', ',']:
                return errors_list.append(_('weekdays invalid'))
    except ValueError:
        errors_list.append(_('weekdays invalid'))


def object_exists(query_set, **kwargs):
    return query_set.objects.filter(**kwargs).exists()


def get_object(query_set, **kwargs):
    return query_set.objects.get(**kwargs)


def _check_required_data(request_data):
    if 'date' in request_data:
        required_data = ['reason', 'date', 'descriptions']
    else:
        required_data = ['reason', 'date_from', 'date_to', 'weekdays', 'descriptions']
    return all(elem in request_data for elem in required_data)


def check_required_data_generic(request_data, required_data):
    return all(elem in request_data for elem in required_data)


def _validate_reason(request_data, errors):
    reason = request_data.get('reason')
    reason_exists = object_exists(models.FoodInclusionReason, name=reason)
    if not reason_exists:
        errors.append(_('reason doesnt exist'))


def _validate_status(request_data, errors):
    status = request_data.get('status')
    status_exists = object_exists(models.FoodInclusionStatus, name=status)
    if 'status' in request_data and not status_exists:
        errors.append(_('status doesnt exist'))


def get_errors_list(request_data):
    errors = list()

    if not _check_required_data(request_data):
        return [_('missing arguments')]

    if not _is_valid_payload(request_data):
        return [_('request_data needs to be a QueryString')]

    _validate_descriptions(request_data, errors)
    _validate_status(request_data, errors)
    _validate_reason(request_data, errors)
    _validate_date_block(request_data, errors)
    return errors


def _is_valid_payload(request_data):
    return request_data and isinstance(request_data, dict)


def _validate_date_block(request_data, errors):
    if 'date' in request_data:
        validate_date_format(request_data.get('date'), errors)
    else:
        validate_date_format(request_data.get('date_from'), errors)
        validate_date_format(request_data.get('date_to'), errors)
        if 'weekdays' in request_data:
            validate_weekdays(request_data.get('weekdays'), errors)


def _validate_descriptions(request_data, errors):
    descriptions = request_data.get('descriptions')
    if not isinstance(descriptions, list):
        errors.append(_('descriptions needs to be a list'))
    if len(descriptions) == 0:
        errors.append(_('descriptions cannot be empty'))
    for description in descriptions:
        meal_type = description.get('meal_type')
        school_period = description.get('school_period')
        number_of_students = description.get('number_of_students')
        meal_exists = object_exists(MealType, name=meal_type)
        school_period_exists = object_exists(SchoolPeriod, name=school_period)

        if not meal_exists:
            errors.append(_('meal type doesnt exist'))
        if not school_period_exists:
            errors.append(_('school period doesnt exist'))
        if not isinstance(number_of_students, int):
            errors.append(_('number of students needs to be int'))
