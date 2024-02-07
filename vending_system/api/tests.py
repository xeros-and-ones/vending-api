from django.test import TestCase, Client
from rest_framework import status
from .models import Product, User
from .serializers import UserSerializer, ViewProductSerializer


class UserCrudTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create(
            username="test_update_user", password="testpassword", role="SELLER"
        )

    def test_create_user(self):
        response = self.client.post(
            "/users/create", {"username": "test_user", "password": "testpassword", "role": "BUYER"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_missing_data(self):
        response = self.client.post(
            "/users/create", {"username": "", "password": "testpassword", "role": "BUYER"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_role(self):
        response = self.client.post(
            "/users/update",
            {
                "username": self.user.username,
                "password": self.user.password,
                "role": "BUYER",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_users(self):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        response = self.client.get("/users/view")
        self.assertEqual(response.data, {"Users": serializer.data})

    def test_delete_user(self):
        response = self.client.post(
            "/users/delete", {"username": self.user.username, "password": self.user.password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductCrudTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.seller = User.objects.create(
            username="test_seller", password="testpassword", role="SELLER", id=15
        )
        self.buyer = User.objects.create(
            username="test_buyer", password="testpassword", role="BUYER"
        )
        self.product = Product.objects.create(
            product_name="mock_product",
            cost=10,
            amount_available=20,
            seller=User.objects.get(pk=self.seller.pk),
        )

    def test_create_product(self):
        response = self.client.post(
            "/products/create",
            {
                "username": self.seller.username,
                "password": self.seller.password,
                "product_name": "test_product",
                "cost": 10,
                "amount_available": 2,
            },
        )
        products = Product.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(len(products), 0)

    def test_view_users(self):
        products = Product.objects.all()
        serializer = ViewProductSerializer(products, many=True)
        response = self.client.get("/products/view")
        self.assertEqual(response.data, {"Products": serializer.data})

    def test_create_product_with_buyer(self):
        response = self.client.post(
            "/products/create",
            {
                "username": self.buyer.username,
                "password": self.buyer.password,
                "product_name": "test_product_with_buyer",
                "cost": 10,
                "amount_available": 2,
            },
        )
        if Product.objects.filter(seller_id=self.buyer.pk):
            product = len(Product.objects.filter(seller_id=self.buyer.pk))
        else:
            product = None
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(product, None)


class ProductUpdateTest(TestCase):
    def setUp(self):
        self.seller = User.objects.create(username="seller", password="sellerpass", role="SELLER")
        self.product = Product.objects.create(
            product_name="Old Product Name", cost=100, amount_available=10, seller=self.seller
        )
        self.client = Client()

    def test_product_update(self):
        response = self.client.put(
            f"/products/{self.product.pk}/update",
            {
                "username": self.seller.username,
                "password": self.seller.password,
                "product_name": "New Product Name",
                "cost": 150,
                "amount_available": 20,
            },
            format="json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.product_name, "New Product Name")
        self.assertEqual(self.product.cost, 150)
        self.assertEqual(self.product.amount_available, 20)

    def test_invalid_credentials(self):
        response = self.client.put(
            f"/products/{self.product.pk}/update",
            {
                "username": "nonexistent",
                "password": "wrongpass",
                "product_name": "New Product Name",
                "cost": 50,
                "amount_available": 20,
            },
            format="json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_update(self):
        # Create another user who is not the seller
        self.another_user = User.objects.create(
            username="another_user", password="another_userpass", role="SELLER"
        )
        response = self.client.put(
            f"/products/{self.product.pk}/update",
            {
                "username": self.another_user.username,
                "password": self.another_user.password,
                "product_name": "New Product Name",
                "cost": 150,
                "amount_available": 20,
            },
            format="json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductDeleteTest(TestCase):
    def setUp(self):
        # Setup a seller user and a product
        self.seller = User.objects.create(username="seller", password="sellerpass", role="SELLER")
        self.product = Product.objects.create(
            product_name="Example Product", cost=100, amount_available=10, seller=self.seller
        )
        self.client = Client()

    def test_product_delete(self):
        response = self.client.post(
            f"/products/{self.product.pk}/delete",
            {"username": self.seller.username, "password": self.seller.password},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.pk).exists())

    def test_invalid_credentials(self):
        response = self.client.post(
            f"/products/{self.product.pk}/delete",
            {"username": "nonexistent", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_delete(self):
        # Create another user who is not the seller
        self.another_user = User.objects.create(
            username="another_user", password="another_userpass", role="SELLER"
        )
        response = self.client.post(
            f"/products/{self.product.pk}/delete",
            {"username": "another_user", "password": "another_userpass"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DepositTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.buyer = User.objects.create(
            username="test_buyer", password="testpassword", role="BUYER"
        )

    def test_successful_deposit(self):
        response = self.client.post(
            "/deposit/",
            {"username": self.buyer.username, "password": self.buyer.password, "deposit": "100"},
        )
        self.assertEqual(User.objects.get(username=self.buyer.username).deposit, 100)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_deposit(self):
        response = self.client.post(
            "/deposit/",
            {"username": self.buyer.username, "password": "wrongpass", "deposit": "100"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_buyer_deposit(self):
        # Create a non-buyer user
        self.non_buyer = User.objects.create(
            username="non_buyer", password="non_buyerpass", role="SELLER"
        )
        response = self.client.post(
            "/deposit/",
            {
                "username": self.non_buyer.username,
                "password": self.non_buyer.password,
                "deposit": "100",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_user_deposit(self):
        response = self.client.post(
            "/deposit/",
            {"username": "nonexistent", "password": "nonexistentpass", "deposit": "100"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResetDepositTest(TestCase):
    def setUp(self):
        self.buyer = User.objects.create(username="buyer", password="buyerpass", role="BUYER")
        self.client = Client()

    def test_reset_deposit(self):
        self.buyer.deposit = 100  # Simulate a previous deposit
        self.buyer.save()
        response = self.client.post("/reset", {"username": "buyer", "password": "buyerpass"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(username="buyer").deposit, 0)

    def test_unauthorized_reset(self):
        response = self.client.post("/reset", {"username": "buyer", "password": "wrongpass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_buyer_reset(self):
        # Create a non-buyer user
        self.non_buyer = User.objects.create(
            username="non_buyer", password="non_buyerpass", role="SELLER"
        )
        response = self.client.post(
            "/reset", {"username": "non_buyer", "password": "non_buyerpass"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BuyProductTest(TestCase):
    def setUp(self):
        self.buyer = User.objects.create(username="buyer", password="buyerpass", role="BUYER")
        self.buyer.deposit = 200
        self.buyer.save()
        self.seller = User.objects.create(username="seller", password="sellerpass", role="SELLER")

        self.product = Product.objects.create(
            product_name="Example Product", cost=100, amount_available=10, seller=self.seller
        )

        self.client = Client()

    def test_successful_purchase(self):
        response = self.client.post(
            "/buy",
            {
                "username": self.buyer.username,
                "password": self.buyer.password,
                "product_id": self.product.pk,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(username="buyer").deposit, 100)
        self.assertEqual(Product.objects.get(pk=self.product.pk).amount_available, 9)

    def test_out_of_stock(self):
        # Reduce the product's availability to zero
        self.product.amount_available = 0
        self.product.save()

        response = self.client.post(
            "/buy",
            {
                "username": self.buyer.username,
                "password": self.buyer.password,
                "product_id": self.product.pk,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_insufficient_funds(self):
        # Adjust the buyer's deposit to be less than the product cost
        self.buyer.deposit = 50
        self.buyer.save()

        response = self.client.post(
            "/buy",
            {
                "username": self.buyer.username,
                "password": self.buyer.password,
                "product_id": self.product.pk,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_attempt(self):
        response = self.client.post(
            "/buy",
            {
                "username": self.buyer.username,
                "password": "wrongPass",
                "product_id": self.product.pk,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
