import requests
import logging

from geopy import distance

from django.shortcuts import render
from django.conf import settings
from .models import Address


def get_geo_objects(apikey, address):
    """Запрашивает геообъекты у Яндекс.Карт"""
    response = requests.get("https://geocode-maps.yandex.ru/1.x", params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    data = response.json()
    feature_members = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
    return feature_members


def get_or_create_address(apikey, address):
    """Возвращает координаты адреса (берёт из БД или запрашивает у API)"""
    obj, created = Address.objects.get_or_create(raw_address=address)

    if not obj.latitude or not obj.longitude:
        geo_objects = get_geo_objects(apikey, address)
        if not geo_objects:
            logging.warning(f'Не удалось найти координаты для адреса: {address}')
            return None

        geo_object = geo_objects[0]['GeoObject']['Point']['pos']
        lon_str, lat_str = geo_object.split()
        obj.latitude, obj.longitude = lat_str, lon_str
        obj.save()

    return (obj.latitude, obj.longitude)


def distance_calculation(first_address, second_address):
    """Считает расстояние между двумя адресами в км"""
    apikey = settings.YANDEX_API_KEY

    first_coords = get_or_create_address(apikey, first_address)
    if not first_coords:
        return None

    second_coords = get_or_create_address(apikey, second_address)
    if not second_coords:
        return None

    return distance.distance(
        (float(first_coords[0]), float(first_coords[1])),
        (float(second_coords[0]), float(second_coords[1]))
    ).km
