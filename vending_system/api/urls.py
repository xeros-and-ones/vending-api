from django.urls import path
from .views import (
    CreateProduct,
    ProductDelete,
    ProductList,
    DeleteUsers,
    Deposit,
    Buy,
    CreateUser,
    ProductUpdate,
    ResetDeposit,
    UpdateUsers,
    ViewUsers,
)

urlpatterns = [
    path("users/create", CreateUser.as_view()),
    path("users/view", ViewUsers.as_view()),
    path("users/delete", DeleteUsers.as_view()),
    path("users/update", UpdateUsers.as_view()),
    path("products/create", CreateProduct.as_view()),
    path("products/view", ProductList.as_view()),
    path("products/<int:product_id>/delete", ProductDelete.as_view()),
    path("products/<int:product_id>/update", ProductUpdate.as_view()),
    path("deposit/", Deposit.as_view()),
    path("reset", ResetDeposit.as_view()),
    path("buy", Buy.as_view()),
]
