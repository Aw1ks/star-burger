from django.urls import path

from .views import product_list_api, banners_list_api, register_order, model_response_order


app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order),

    path('api/order/', model_response_order, name='api_order')
]
