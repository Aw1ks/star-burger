import json

from django.http import JsonResponse
from django.templatetags.static import static
from pprint import pprint

from .models import Product, Order, OrderProducts


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


def register_order(request):
    data = json.loads(request.body.decode())
    pprint(data)

    address = data.get('address', '').strip()
    firstname = data.get('firstname', '').strip()
    lastname = data.get('lastname', '').strip()
    phonenumber = data.get('phonenumber', '').strip()

    products_info = data.get('products', [])

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

    return JsonResponse({})
