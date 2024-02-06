from rest_framework.views import APIView, Response
from .serializers import (
    ProductSerializer,
    UserSerializer,
    DepositSerializer,
    ResetDepositSerializer,
)
from .models import User, Product
from rest_framework.response import Response
from rest_framework import status


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


class Deposit(APIView):
    serializer_class = DepositSerializer

    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        if user and user.password == request.data["password"]:
            if user.role == "BUYER":
                user.deposit = request.data["deposit"]
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
                {"Message": "something wrong happend"},
                status=status.HTTP_400_BAD_REQUEST,
            )
