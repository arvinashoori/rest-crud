from django.shortcuts import render

from rest_framework import serializers
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Category, Product, CartItem, Order, OrderItem
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, UserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category'] 
    search_fields = ['name', 'description'] 

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cart_items = CartItem.objects.filter(user=self.request.user)
        if not cart_items:
            raise serializers.ValidationError("سبد خرید خالی است.")

        order = serializer.save(user=self.request.user, total_amount=self.calculate_total(cart_items))
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, unit_price=item.product.price)
            item.product.stock -= item.quantity
            item.product.save()
        cart_items.delete() 

    def calculate_total(self, cart_items):
        total = 0
        for item in cart_items:
            total += item.product.price * item.quantity
        return total

class UserViewSet(viewsets.ReadOnlyModelViewSet): 
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
