from rest_framework.views import APIView, Response
from .serializers import (
    DeleteProductSerializer,
    ProductBuySerializer,
    UserCrudSerialzer,
    ProductSerializer,
    UserSerializer,
    DepositSerializer,
    ResetDepositSerializer,
    ViewProductSerializer,
)
from .models import User, Product
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404


class CreateUser(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "Message": f"{user.username}, you have been successfully registered as a {user.role}."
                }
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewUsers(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        users = User.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response({"Users": serializer.data})


class DeleteUsers(APIView):
    serializer_class = UserCrudSerialzer

    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        if user:
            if user.password == request.data["password"]:
                user.delete()
                return Response(
                    {"Message": f"{user.username} has been deleted Successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"Message": f"username and/or password don't match"})
        else:
            return Response({"Message": f"{user.username} doesn't appear to be in the database"})


class UpdateUsers(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        if user:
            if user.password == request.data["password"]:
                user.role = request.data["role"]
                user.save()
                return Response(
                    {"Message": f"{user.username}'s Record has been Updated Successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"Message": f"username and/or password don't match"})
        else:
            return Response({"Message": f"{user.username} doesn't appear to be in the database"})


class CreateProduct(APIView):
    serializer_class = ProductSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if User.objects.get(username=request.data["username"]).role == "SELLER":
                seller = User.objects.get(username=request.data["username"])
                product_name = request.data["product_name"]
                cost = request.data["cost"]
                amount_available = request.data["amount_available"]
                prod = Product(
                    seller=seller,
                    product_name=product_name,
                    cost=cost,
                    amount_available=amount_available,
                )
                prod.save()
                return Response(
                    {
                        "Message": f"Product {request.data['product_name']} Record has been Added Successfully"
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"Message": "User Doesn't Appear to be A Seller"})

        else:
            return Response({"Message": "something Went Wrong"})


class ProductDelete(APIView):
    serializer_class = DeleteProductSerializer

    def post(self, request, product_id):
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.get(username=username)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        # Check if the authenticated user is the seller of the product
        if product.seller != user:
            return Response(
                {"detail": "You do not have permission to delete this product."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Delete the product
        if user.password == password:
            product.delete()
            return Response(
                {"Message": f"Product {product.product_name} Removed Successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"Message": f"username and/or password don't match"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class ProductList(APIView):
    serializer_class = ViewProductSerializer

    def get(self, request):
        products = Product.objects.all()
        serializer = self.serializer_class(products, many=True)
        return Response({"Products": serializer.data})


class ProductUpdate(APIView):
    serializer_class = ProductSerializer

    def put(self, request, product_id):
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.get(username=username)
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        if product.seller != user:
            return Response(
                {"detail": "You do not have permission to delete this product."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Delete the product
        if user.password == password:
            product.product_name = request.data["product_name"]
            product.cost = request.data["cost"]
            product.amount_available = request.data["amount_available"]
            product.save()
            return Response(
                {"Message": f"Product {product.product_name} Updated Successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"Message": f"username and/or password don't match"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class Deposit(APIView):
    serializer_class = DepositSerializer

    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        if user and user.password == request.data["password"]:
            if user.role == "BUYER":
                user.deposit += int(request.data["deposit"])
                user.save()
                return Response(
                    {
                        "Message": f"{user.username}, you have successfully added {request.data['deposit']} your balance is {user.deposit}."
                    }
                )
            else:
                return Response({"Message": f"{user.username} doesn't appear to be a buyer"})
        else:
            return Response(
                {"Message": "something wrong happend"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetDeposit(APIView):
    serializer_class = ResetDepositSerializer

    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        if user and user.password == request.data["password"]:
            if user.role == "BUYER":
                user.deposit = 0
                user.save()
                return Response(
                    {"Message": f"{user.username}'s deposit has been reset"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"Message": f"{user.username} doesn't appear to be a buyer"})
        else:
            return Response(
                {"Message": "Something Wrong with Credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )


def represent_change_with_coins(value):
    coins = [100, 50, 20, 10, 5]
    result = {}
    for coin in coins:
        count = value // coin
        if count > 0:
            result[coin] = count
            value -= count * coin
    return result


class Buy(APIView):
    serializer_class = ProductBuySerializer

    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        if user and user.password == request.data["password"]:
            if user.role == "BUYER":
                product = Product.objects.get(pk=request.data["product_id"])
                price = product.cost
                amount = int(request.data["amount"])
                total = price * amount
                if product.amount_available <= 0:
                    return Response({"Message": f"{product.product_name} is out of stock"})
                if user.deposit >= total:
                    user.deposit -= total
                    user.save()
                    product.amount_available -= amount
                    product.save()
                    change = represent_change_with_coins(user.deposit)
                    return Response(
                        {
                            "Success": f"you bought {amount} {product.product_name}. the total was {total} and the remaining is {change}"
                        }
                    )
                else:
                    return Response(
                        {"Message": f"Not enough funds, You're short of {total - user.deposit}"}
                    )
            else:
                return Response({"Message": f"{user.username} doesn't appear to be a buyer"})
        else:
            return Response(
                {"Message": "Something Wrong with Credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )
