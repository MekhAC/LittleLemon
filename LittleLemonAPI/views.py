from datetime import datetime

from django.contrib.auth.models import Group, User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import Cart, MenuItem, Order
from .serializers import (
    CartSerializer,
    MenuItemSerializer,
    OrderItemSerializer,
    OrderSerializer,
)


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category = request.query_params.get('category')
        if(category):
            items = items.filter(category__slug=category)
        search = request.query_params.get('search')
        if(search):
            items = items.filter(title__icontains=search)
        ordering = request.query_params.get('ordering')
        if(ordering):
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)
        page = request.query_params.get('page',1)
        perpage = request.query_params.get('page_size',10)
        try:
            paginator = Paginator(items, per_page=min(int(perpage),50))
            items = paginator.page(number = page)
        except (EmptyPage, PageNotAnInteger, ValueError):
            return Response({"error": "Invalid pagination parameters"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        if not request.user.groups.filter(name='Manager').exists():
            return Response({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST', 'PUT', 'DELETE','PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def menu_item_single(request, pk):
    try:
        item = MenuItem.objects.get(pk=pk)
    except MenuItem.DoesNotExist:
        return Response({"error": "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method in ['PUT', 'PATCH']:
        if not request.user.groups.filter(name='Manager').exists():
            return Response({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(item, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        if not request.user.groups.filter(name='Manager').exists():
            return Response({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(item)
        item.delete()
        return Response({"item": serializer.data, "message": "Menu item deleted"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def manager_users(request):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)
    else:
        group = Group.objects.get(name='Manager')
        if request.method == 'GET':
            users = User.objects.filter(groups=group)
            managers = []
            for user in users:
                managers.append({
                    "id": user.pk,
                    "username": user.username,
                })
            return Response(managers, status=status.HTTP_200_OK)
        if request.method == 'POST':
            username = request.data.get('username')
            if not username:
                return Response({"error": "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            user.groups.add(group)
            return Response({"message": "New manager added"}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def manager_user_single(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)
    group = Group.objects.get(name='Manager')
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if not user.groups.filter(name='Manager').exists():
        return Response({"error": "User is not a manager"}, status=status.HTTP_400_BAD_REQUEST)
    user.groups.remove(group)
    return Response({"message": "Manager removed"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def delivery_crew_users(request):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)
    else:
        group = Group.objects.get(name='Delivery Crew')
        if request.method == 'GET':
            users = User.objects.filter(groups=group)
            delivery_crew = []
            for user in users:
                delivery_crew.append({
                    "id": user.pk,
                    "username": user.username,
                })
            return Response(delivery_crew, status=status.HTTP_200_OK)
        if request.method == 'POST':
            username = request.data.get('username')
            if not username:
                return Response({"error": "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            user.groups.add(group)
            return Response({"message": "New delivery crew member added"}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def delivery_crew_user_single(request, pk):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)
    group = Group.objects.get(name='Delivery Crew')
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if not user.groups.filter(name='Delivery Crew').exists():
        return Response({"error": "User is not a delivery crew member"}, status=status.HTTP_400_BAD_REQUEST)
    user.groups.remove(group)
    return Response({"message": "Delivery crew member removed"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def cart_items(request):
    if request.method == 'GET':
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        menuitem_id = request.data.get('menuitem')
        if not menuitem_id:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "Invalid Request"}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart.objects.filter(user=request.user, menuitem=menuitem).first()
        if cart:
            cart_data = {
                "user": request.user.id,
                "menuitem" : menuitem.pk,
                "quantity" : cart.quantity + 1,
                "unit_price" : cart.unit_price,
                "price" : (cart.quantity + 1) * cart.unit_price
            }
            serializer = CartSerializer(cart, data = cart_data)
        else:
            cart_data = {
                "user": request.user.id,
                "menuitem": menuitem.pk,
                "quantity": 1,
                "unit_price": menuitem.price,
                "price": menuitem.price
            }
            serializer = CartSerializer(data = cart_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data , "message": "Cart item added"}, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def orders(request):
    if request.method == 'GET':
        if request.user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif request.user.groups.filter(name='Delivery Crew').exists():
            orders = Order.objects.filter(delivery_crew=request.user)
        else:
            orders = Order.objects.filter(user=request.user)
        ordering = request.query_params.get('ordering')
        if ordering:
            ordering_fields = ordering.split(',')
            orders = orders.order_by(*ordering_fields)
        page = request.query_params.get('page',1)
        perpage = request.query_params.get('page_size',10)
        try:
            paginator = Paginator(orders, per_page=min(int(perpage),50))
            orders = paginator.page(number = page)
        except (EmptyPage, PageNotAnInteger, ValueError):
            return Response({"error": "Invalid pagination parameters"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user).select_related("menuitem")
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        total = sum(item.quantity * item.unit_price for item in cart_items)
        orderSerializer = OrderSerializer(data={
            "user": request.user.id,
            "status": False,
            "total": total,
            "date": datetime.now().date()
        })
        if not orderSerializer.is_valid():
            return Response(orderSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.create(
            user=request.user,
            status=False,
            total=total,
            date=datetime.now().date()
        )
        order_id = order.pk
        for item in cart_items:
            item_price = item.unit_price * item.quantity
            itemSerializer = OrderItemSerializer(data = {
                "order": order_id,
                "menuitem": item.menuitem.pk,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "price": item_price,
            })
            if not itemSerializer.is_valid():
                Order.objects.filter(id = order_id).delete()
                return Response(itemSerializer.errors, status = status.HTTP_400_BAD_REQUEST)
            itemSerializer.save()
        return Response(orderSerializer.data , status = status.HTTP_201_CREATED)
    




@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def order_single(request, pk):
    try:
        order = Order.objects.get(pk = pk)
    except Order.DoesNotExist:
        return Response({"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = OrderSerializer(order)
        if request.user.groups.filter(name="Manager").exists():
            return Response(serializer.data, status = status.HTTP_200_OK)
        elif request.user.groups.filter(name="Delivery Crew").exists():
            if order.delivery_crew != request.user:
                return Response( {"error": "You are not assigned to this order."},status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(serializer.data, status = status.HTTP_200_OK)
        elif request.user == order.user:
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response( {"error": "Authorization required"},status=status.HTTP_403_FORBIDDEN)
    if request.method == 'DELETE':
        if request.user.groups.filter(name="Manager").exists():
            serializer = OrderSerializer(order)
            order.delete()
            return Response ({"order": serializer.data, "message": "Order deleted"}, status=status.HTTP_200_OK)
        return Response ({"error": "Authorization required"},status=status.HTTP_403_FORBIDDEN)
    if request.method in ['PUT' , 'PATCH']:
        if request.user.groups.filter(name="Manager").exists():
            serializer = OrderSerializer(order , data = request.data, partial = (request.method == 'PATCH'))
            if serializer.is_valid:
                serializer.save()
                return Response (serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        elif request.user.groups.filter(name="Delivery Crew").exists():
            if order.delivery_crew != request.user:
                return Response ({"error": "You are not assigned to this order"}, status = status.HTTP_403_FORBIDDEN)
            if set(request.data.keys()) != {"status"}:
                return Response ({"error": "Only status can be modified"}, status = status.HTTP_403_FORBIDDEN)
            serializer = OrderSerializer(order, data = {"status" : request.data("status")}, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Order status changed", "status": request.data["status"]}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        return Response ({"error": "Authorization required"}, status=status.HTTP_403_FORBIDDEN)


