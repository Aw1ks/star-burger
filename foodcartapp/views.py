import json

from django.http import JsonResponse
from django.templatetags.static import static

from .models import Product, Order, OrderProducts
from .serializers import OrderSerializer

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
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
    if not request.data:
        return Response({'error': 'Пустое тело запроса'}, status=status.HTTP_400_BAD_REQUEST)

    order_info = request.data
    pprint(order_info)

    address = order_info.get('address', '').strip()
    firstname = order_info.get('firstname', '').strip()
    lastname = order_info.get('lastname', '').strip()
    phonenumber = order_info.get('phonenumber', '').strip()

    products_info = order_info.get('products', [])
    if not isinstance(products_info, list) or not products_info:
        return Response({'error': 'Неверный формат json. Ключ products пуст/не указан либо не является list.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    order = Order.objects.create(
        name=firstname,
        surname=lastname,
        address=address,
        phone_number=phonenumber
    )

    for item in products_info:
        product_id = item.get('product')
        quantity = item.get('quantity')

        product = Product.objects.get(pk=product_id)

        OrderProducts.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )

    return Response({'status': 'success'})


@api_view(['GET'])
def model_response_order(request):
    if request.method == 'GET':
        order = Order.objects.all()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
