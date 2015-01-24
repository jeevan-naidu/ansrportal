from django.core.cache import cache

from .models import Holiday
from . import locationcache as locations


def initHolidayCache():
    for alocation in locations.getLocations():
        HOLIDAYCACHEID = 'ANSR:holidays:' + str(alocation['id'])
        if cache.get(HOLIDAYCACHEID) is None:
            cache.set(
                HOLIDAYCACHEID,
                Holiday.objects.filter(
                    location_id=alocation['id']).order_by('date').values(
                    'id',
                    'date',
                    'location'))


def getLocationHolidays(locationid):
    initHolidayCache()
    return cache.get('ANSR:holidays:' + str(locationid))


def getUserHolidays(user):
    initHolidayCache()
    holidays = []
    if hasattr(user, 'employee'):
        holidays = getLocationHolidays(user.employee.location.id)
    return holidays


def getUserHolidaysBetween(user, startDate, endDate):
    initHolidayCache()
    holidays = []
    if hasattr(user, 'employee'):
        alldays = getLocationHolidays(user.employee.location.id)
        for aday in alldays:
            if startDate <= aday['date'] and aday['date'] <= endDate:
                holidays.append(aday['date'])
    return holidays
