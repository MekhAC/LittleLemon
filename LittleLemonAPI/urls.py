from django.urls import path

from . import views

urlpatterns = [
    path('menu-items/', views.menu_items, name='menu-items'), 
    path('menu-items/<int:pk>/', views.menu_item_single, name='menu-item-single'),
    path('groups/manager/users/', views.manager_users, name='manager-users'),
    path('groups/manager/users/<int:pk>/', views.manager_user_single, name='manager-user-single'),
    path('groups/delivery-crew/users/', views.delivery_crew_users, name='delivery-crew-users'),
    path('groups/delivery-crew/users/<int:pk>/', views.delivery_crew_user_single, name='delivery-crew-user-single'),
    path('cart/menu-items/', views.cart_items, name='cart-items'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/', views.order_single, name='order-single'),
]