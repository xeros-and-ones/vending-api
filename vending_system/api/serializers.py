from django.forms import fields
from rest_framework import serializers
from .models import User, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "role"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["seller_id", "amount_available", "cost", "product_name"]


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "deposit"]


class ResetDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
