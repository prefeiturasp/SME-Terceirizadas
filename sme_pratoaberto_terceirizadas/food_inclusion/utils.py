import datetime

from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.common_data.utils import get_working_days_after
from sme_pratoaberto_terceirizadas.food.models import MealType
from sme_pratoaberto_terceirizadas.food_inclusion import models


def validate_date_format(date_text, errors_list):
    try:
        return datetime.datetime.strptime(date_text, '%d/%m/%Y')
    except ValueError:
        errors_list.append(_('incorrect data format, should be DD/MM/YYYY'))


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
    required_data = ['day_reasons']
    return all(elem in request_data for elem in required_data)


def check_required_data_generic(request_data, required_data):
    return all(elem in request_data for elem in required_data)


def _validate_reason(request_data, errors):
    reason = request_data.get('reason')
    reason_exists = object_exists(models.FoodInclusionReason, name=reason)
    if not reason_exists:
        errors.append(_('Motivo não existe'))


def _validate_status(request_data, errors):
    status = request_data.get('status')
    status_exists = object_exists(models.FoodInclusionStatus, name=status)
    if 'status' in request_data and not status_exists:
        errors.append("Status não existe")


def get_errors_list(request_data):
    errors = list()

    if not _check_required_data(request_data):
        return ['Parâmetros faltando']

    if not _is_valid_payload(request_data):
        return ['Formato de requisição inválido']

    _validate_descriptions(request_data, errors)
    _validate_status(request_data, errors)
    _validate_date_block(request_data, errors)
    return errors


def _is_valid_payload(request_data):
    return request_data and isinstance(request_data, dict)


def _validate_date_block(request_data, errors):
    day_reasons = request_data.get('day_reasons')
    for day_reason in day_reasons:
        _validate_reason(day_reason, errors)
        if day_reason.get('date', None):
            _datetime = validate_date_format(day_reason.get('date'), errors)
            if _datetime and _datetime.date() < get_working_days_after(2):
                errors.append('Mínimo de 2 dias úteis para fazer o pedido')
        else:
            validate_date_format(day_reason.get('date_from'), errors)
            validate_date_format(day_reason.get('date_to'), errors)
            if 'weekdays' in request_data:
                validate_weekdays(day_reason.get('weekdays'), errors)


def _validate_description(description, errors):
    meal_types = description.get('select') if isinstance(description.get('select'), list) else [
        description.get('select')]
    print(meal_types)
    number_of_students = description.get('number')
    for meal_type in meal_types:
        if not object_exists(MealType, name=meal_type):
            errors.append('Tipo de refeição não existe')
    if not number_of_students.isdigit():
        errors.append('Número de estudantes precisa vir como inteiro')


def _validate_descriptions(request_data, errors):
    description_first_period = request_data.get('description_first_period', None)
    description_second_period = request_data.get('description_second_period', None)
    description_third_period = request_data.get('description_third_period', None)
    description_fourth_period = request_data.get('description_fourth_period', None)
    description_integrate = request_data.get('description_integrate', None)
    if not (description_first_period or description_second_period or description_third_period
            or description_fourth_period or description_integrate):
        errors.append("Obrigatório ao menos um período")
    if description_first_period:
        _validate_description(description_first_period, errors)
    if description_second_period:
        _validate_description(description_second_period, errors)
    if description_third_period:
        _validate_description(description_third_period, errors)
    if description_fourth_period:
        _validate_description(description_fourth_period, errors)
    if description_integrate:
        _validate_description(description_integrate, errors)
