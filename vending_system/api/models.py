from django.db import models


class User(models.Model):
    ROLE_CHOICES = [("BUYER", "Buyer"), ("SELLER", "Seller")]
    DEPOSIT_CHOICES = [(5, "5"), (10, "10"), (20, "20"), (50, "50"), (100, "100")]

    username = models.CharField(
        unique=True,
        max_length=30,
        null=False,
    )
    password = models.CharField(max_length=50, null=False)
    deposit = models.IntegerField(choices=DEPOSIT_CHOICES, null=True)
    role = models.CharField(choices=ROLE_CHOICES, default="BUYER", max_length=20)

    def __str__(self) -> str:
        return f"username: {self.username} \n" f"deposit: {self.deposit} \n" f"Role: {self.role} \n"


class Product(models.Model):
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_available = models.IntegerField()
    cost = models.IntegerField()
    product_name = models.CharField(null=False, max_length=30)

    def __str__(self) -> str:
        return (
            f"seller_id: {self.seller_id} \n"
            f"amount available: {self.amount_available} \n"
            f"cost: {self.cost} \n"
            f"product name: {self.product_name}"
        )
