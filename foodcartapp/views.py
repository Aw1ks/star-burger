import json
import re

from django.http import JsonResponse
from django.templatetags.static import static

from .models import Product, Order, OrderProducts
from .serializers import OrderSerializer

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.renderers import JSONRenderer
from pprint import pprint


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_order(request):
    order_info = request.data
    pprint(order_info)

    serializer = OrderSerializer(data=order_info)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=str(order_info['firstname']),
        lastname=str(order_info['lastname']),
        phonenumber=str(order_info['phonenumber']),
        address=str(order_info['address']),
    )

    order_product_fields = serializer.validated_data['products']
    order_product = [OrderProducts(order=order, **fields) for fields in order_product_fields]
    OrderProducts.objects.bulk_create(order_product)

    serialized_info = serializer.data
    serialized_info['id'] = order.id
    return Response(serialized_info)


@api_view(['GET'])
def model_response_order(request):
    if request.method == 'GET':
        order = Order.objects.all()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
