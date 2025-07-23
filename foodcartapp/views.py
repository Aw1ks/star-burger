import json
import re

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
        return Response({'error': 'Пустое тело запроса', 'field': 'body'}, status=status.HTTP_400_BAD_REQUEST)

    order_info = request.data
    pprint(order_info)

    required_fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']
    missing_fields = []

    for field in required_fields:
        if field not in order_info:
            missing_fields.append(field)

    if missing_fields:
        missing_fields_all = ', '.join(missing_fields)
        return Response({'error': f'Нет обязательных полей: {missing_fields_all}.', 'fields': missing_fields}, status=status.HTTP_400_BAD_REQUEST)

    firstname = order_info.get('firstname')
    lastname = order_info.get('lastname')
    phonenumber = order_info.get('phonenumber')
    address = order_info.get('address')
    products_info = order_info.get('products')

    null_fields_value = []

    for field_name, field_value in [('firstname', firstname), ('lastname', lastname), ('phonenumber', phonenumber), ('address', address)]:
        if not isinstance(field_value, str) or not field_value.strip():
            null_fields_value.append(field_name)

    if null_fields_value:
        null_fields_all = ', '.join(null_fields_value)
        return Response({'error': 'Эти поля не могут быть пустыми: {}.'.format(null_fields_all), 'field': null_fields_all}, status=status.HTTP_400_BAD_REQUEST)

    phone_pattern = r'^\+\d{11}$'
    if not re.match(phone_pattern, phonenumber):
        return Response({'error': 'Введен некорректный номер телефона.', 'field': 'phonenumber'}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(products_info, list):
        return Response({'error': 'Неверный формат json. Ключ products не является списком.', 'field': 'products'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if len(products_info) == 0:
        return Response({'error': 'products: Этот список не может быть пустым.', 'field': 'products'}, status=status.HTTP_400_BAD_REQUEST)

    for item in products_info:
        if not isinstance(item, dict):
            return Response({'error': 'Каждый элемент products должен быть объектом.', 'field': 'products'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        product_id = item.get('product')
        quantity = item.get('quantity')

        if product_id is None:
            return Response({'error': 'products: Недопустимый первичный ключ "None".', 'field': 'products'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if quantity is None:
            return Response({'error': 'products: Отсутствует ключ "quantity".', 'field': 'products'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if not isinstance(product_id, int):
            return Response({'error': 'products: Неверный тип id продукта.', 'field': 'products'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if not isinstance(quantity, int):
            return Response({'error': 'products: Неверный тип количества.', 'field': 'products'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        from .models import Product, Order, OrderProducts
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': f'products: Недопустимый первичный ключ "{product_id}".', 'field': 'products'}, status=status.HTTP_406_NOT_ACCEPTABLE)

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
