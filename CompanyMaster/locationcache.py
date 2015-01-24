from django.core.cache import cache

from .models import OfficeLocation


def initLocationCache():
    if cache.get('ANSR:locations') is None:
        cache.set(
            'ANSR:locations',
            list(
                OfficeLocation.objects.all().values(
                    'id',
                    'name',
                    'city',
                    'state',
                    'zipcode')))


def getLocations():
    initLocationCache()
    return cache.get('ANSR:locations')


def getLocation(locationid):
    initLocationCache()
    for location in cache.get('ANSR:locations'):
        if location['id'] == locationid:
            return location
    return None
