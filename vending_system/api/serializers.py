from django.core import validators
from django.forms import fields
from rest_framework import serializers
from .models import User, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "role"]


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "deposit"]


class ResetDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]


class UserCrudSerialzer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]


class ProductSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = Product
        fields = ["username", "password", "product_name", "cost", "amount_available"]


class ViewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "product_name", "cost", "amount_available"]


class DeleteProductSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ProductBuySerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    product_id = serializers.IntegerField()
    amount = serializers.IntegerField()
