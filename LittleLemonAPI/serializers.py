from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Cart, Category, MenuItem, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        extra_kwargs = {
            'price': {'min_value': Decimal('0.00')},
        }

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
        extra_kwargs = {
            "user": {
                "required": False
            },
            "quantity": {
                "min_value": 1
            },
            "unit_price": {
                "min_value": 0
            },
            "price": {
                "min_value": 0
            }
        }

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs = {
            'unit_price': {'min_value': Decimal('0.00')},
            'quantity': {'min_value': 1},
            'price': {'min_value': Decimal('0.00')},
        }