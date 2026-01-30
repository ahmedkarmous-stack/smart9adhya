from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('', views.order_list, name='list'),
    path('<str:order_id>/', views.order_detail, name='detail'),
    path('<str:order_id>/refund/', views.refund_request, name='refund'),
    path('refunds/', views.refund_list, name='refunds'),
]
