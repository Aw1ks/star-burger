from rest_framework import serializers
from .models import Order, OrderProduct

class OrderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity', 'price']
        read_only_fields = ['price']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductsSerializer(many=True, write_only=True, allow_empty=False)

    class Meta:
        model = Order
        fields = [
            'id', 
            'firstname', 
            'lastname', 
            'phonenumber', 
            'address', 
            'products'
        ]

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        order_products = [
            OrderProduct(
                order=order,
                product=product['product'],
                quantity=product['quantity'],
                price=product['product'].price
            ) for product in products
        ]
        OrderProduct.objects.bulk_create(order_products)

        return order