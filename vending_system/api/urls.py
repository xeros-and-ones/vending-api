from django.urls import path
from .views import Deposit, CreateUser, ResetDeposit

urlpatterns = [
    path("deposit/", Deposit.as_view()),
    path("create", CreateUser.as_view()),
    path("reset", ResetDeposit.as_view()),
]
