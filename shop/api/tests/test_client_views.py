# from django.test import TestCase
# from rest_framework.test import APITestCase
# from rest_framework import status
# from api.models import (
#     Category,
#     Discount,
#     Promocode,
#     Producer,
#     ProductItem,
#     RegistredUser,
#     Basket,
# )
# from django.urls import reverse
# from .factories import (
#     CategoryFactory,
#     DiscountFactory,
#     PromocodeFactory,
#     ProducerFactory,
#     ProductItemFactory,
#     RegistredUserFactory,
#     BasketFactory,
#     CashbackFactory,
# )
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from ..tokens import account_activation_token
# from datetime import datetime, timedelta
# import time_machine
# from django.conf import settings


# class TestCategoriesView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.categories = CategoryFactory.create_batch(5)

#     def test_category_all_view(self):
#         response = self.client.get(reverse("categories-all"))
#         self.assertIsInstance(response.data, list)
#         self.assertEqual(len(response.data), 5)
#         test_category = Category.objects.get(pk=response.data[0]["id"])
#         self.assertEqual(response.data[0]["name"], test_category.name)
#         self.assertEqual(
#             response.data[0]["description"], test_category.description
#         )


# class TestDiscountsView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.discounts = DiscountFactory.create_batch(5)

#     def test_discount_all_view(self):
#         response = self.client.get(reverse("discounts-all"))
#         self.assertIsInstance(response.data, list)
#         self.assertEqual(len(response.data), 5)
#         test_discount = Discount.objects.get(pk=response.data[0]["id"])
#         self.assertEqual(response.data[0]["name"], test_discount.name)
#         self.assertEqual(response.data[0]["percent"], test_discount.percent)


# class TestPromocodesView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.promocodes = PromocodeFactory.create_batch(5)

#     def test_promocode_all_view(self):
#         response = self.client.get(reverse("promocodes-all"))
#         self.assertIsInstance(response.data, list)
#         self.assertEqual(len(response.data), 5)
#         test_discount = Promocode.objects.get(pk=response.data[0]["id"])
#         self.assertEqual(response.data[0]["percent"], test_discount.percent)
#         self.assertEqual(
#             response.data[0]["is_allowed_to_sum_with_discounts"],
#             test_discount.is_allowed_to_sum_with_discounts,
#         )


# class TestProducersView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.producers = ProducerFactory.create_batch(5)

#     def test_producer_all_view(self):
#         response = self.client.get(reverse("producers-all"))
#         self.assertIsInstance(response.data, list)
#         self.assertEqual(len(response.data), 5)
#         test_producer = Producer.objects.get(pk=response.data[0]["id"])
#         self.assertEqual(response.data[0]["name"], test_producer.name)


# class TestProductItemsView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.categories = CategoryFactory.create_batch(5)
#         cls.discounts = DiscountFactory.create_batch(5)
#         cls.producers = ProducerFactory.create_batch(5)
#         cls.products = []
#         for category, discount, producer in zip(
#             cls.categories, cls.discounts, cls.producers,
#         ):
#             product = ProductItemFactory(
#                 category=category, discount=discount, producer=producer,
#             )
#             cls.products.append(product)

#     def test_product_all_view(self):
#         response = self.client.get(reverse("products-all"))
#         self.assertIsInstance(response.data, list)
#         self.assertEqual(len(response.data), 5)
#         test_product = ProductItem.objects.get(pk=response.data[0]["id"])
#         self.assertEqual(response.data[0]["name"], test_product.name)
#         self.assertEqual(
#             response.data[0]["price"],
#             test_product.price,
#         )
#         self.assertEqual(
#             response.data[0]["category"]["id"], test_product.category.id
#         )


# class TestCategoryProductsView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.categories = CategoryFactory.create_batch(2)
#         cls.products_first_catigory = ProductItemFactory.create_batch(
#             3,
#             category=cls.categories[0],
#             producer=ProducerFactory(),
#             discount=None,
#         )
#         cls.products_second_category = ProductItemFactory.create_batch(
#             2,
#             category=cls.categories[1],
#             producer=ProducerFactory(),
#             discount=None,
#         )

#     def test_category_product_view(self):
#         response = self.client.get(
#             reverse("category-by-id", args=[self.categories[0].id])
#         )
#         self.assertEqual(len(response.data), len(self.products_first_catigory))

#         response = self.client.get(
#             reverse("category-by-id", args=[self.categories[1].id])
#         )
#         self.assertEqual(
#             len(response.data), len(self.products_second_category),
#         )


# class TestProducerProductsView(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.producers = ProducerFactory.create_batch(2)
#         cls.products_first_category = ProductItemFactory.create_batch(
#             3,
#             category=CategoryFactory(),
#             producer=cls.producers[0],
#             discount=None,
#         )
#         cls.products_second_category = ProductItemFactory.create_batch(
#             2,
#             category=CategoryFactory(),
#             producer=cls.producers[1],
#             discount=None,
#         )

#     def test_category_product_view(self):
#         response = self.client.get(
#             reverse("producer-by-id", args=[self.producers[0].id])
#         )
#         self.assertEqual(len(response.data), len(self.products_first_category))

#         response = self.client.get(
#             reverse("producer-by-id", args=[self.producers[1].id])
#         )
#         self.assertEqual(
#             len(response.data), len(self.products_second_category),
#         )


# class TestDiscountrProductsView(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = RegistredUserFactory.create(is_active=True)
#         cls.discounts = DiscountFactory.create_batch(2)
#         cls.products = ProductItemFactory.create_batch(
#             3,
#             category=CategoryFactory(),
#             producer=ProducerFactory(),
#             discount=cls.discounts[0],
#         )
#         cls.products = ProductItemFactory.create_batch(
#             2,
#             category=CategoryFactory(),
#             producer=ProducerFactory(),
#             discount=cls.discounts[1],
#         )

#     def test_discount_product_view(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(
#             reverse("discount-by-id", args=[self.discounts[0].id])
#         )
#         self.assertEqual(len(response.data), 3)

#         response = self.client.get(
#             reverse("discount-by-id", args=[self.discounts[1].id])
#         )
#         self.assertEqual(len(response.data), 2)


# class TestRegistrationView(APITestCase):
#     def test_registration_view(self):

#         data = {
#             "user": {
#                 "email": "milk@test.ts",
#                 "login": "Dea Moon",
#                 "password": "vbiOpcen539ivb",
#                 "age": 19,
#                 "phone": "80298753",
#             }
#         }

#         response = self.client.post(
#             reverse("registration"), data, format="json"
#         )
#         self.assertIn("token", response.data)
#         user = RegistredUser.objects.get(email="milk@test.ts")
#         self.assertEqual(response.data["phone"], user.phone)


# class TestActivateAccountView(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = RegistredUserFactory.create()
#         cls.uid = urlsafe_base64_encode(force_bytes(cls.user.pk))
#         cls.token = account_activation_token.make_token(cls.user)

#     def _get_activate_url(self):
#         return reverse("activate", args=[self.uid, self.token])

#     def test_activate_account_view(self):
#         response = self.client.get(self._get_activate_url())
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_activate_expire_token(self):
#         exp_date = datetime.now() + timedelta(
#             days=settings.PASSWORD_RESET_TIMEOUT + 1
#         )
#         with time_machine.travel(exp_date):
#             response = self.client.get(self._get_activate_url())
#             self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# class TestLoginView(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.password = "qweawefwf31bBi"
#         cls.user = RegistredUserFactory.create(
#             password=cls.password, is_active=True
#         )

#     def test_login_view(self):
#         data = {"user": {"password": self.password, "phone": self.user.phone}}
#         response = self.client.post(reverse("login"), data, format="json")
#         self.assertIn("token", response.data)
#         self.assertEqual(response.data["phone"], self.user.phone)


# class TestBasketView(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = RegistredUserFactory(is_active=True)
#         cls.producers = ProducerFactory()
#         cls.category = CategoryFactory()
#         cls.discounts = DiscountFactory()
#         cls.product = ProductItemFactory()
#         cls.basket = BasketFactory(user=cls.user, product=cls.product)

#     def test_get_basket_view(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(reverse("basket"))
#         result_price = round(response.data["result_price"], 3)
#         basket = Basket.objects.get(user=self.user)
#         result_price_check = float(
#             round(
#                 (
#                     basket.product.price
#                     - (
#                         basket.product.price
#                         * basket.product.discount.percent
#                         / 100
#                     )
#                 )
#                 * basket.number_of_item,
#                 3,
#             )
#         )
#         self.assertEqual(result_price, result_price_check)
#         self.assertEqual(
#             response.data["products"][0]["number_of_item"],
#             basket.number_of_item,
#         )

#     def test_post_basket_view(self):
#         self.client.force_authenticate(user=self.user)
#         data = {"product_id": self.product.id, "number_of_item": 3}
#         response = self.client.post(reverse("basket"), data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_delete_basket_view(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.delete(
#             reverse("basket"), data={"product_id": self.product.id}
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertFalse(Basket.objects.filter(user=self.user).exists())


# class TestCreateOrderView(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = RegistredUserFactory(is_active=True)
#         # cls.cashback = CashbackFactory()
#         cls.products_first_category = ProductItemFactory.create_batch(
#             3,
#             category=CategoryFactory(),
#             producer=ProducerFactory(),
#             discount=DiscountFactory(),
#         )
#         cls.products_second_category = ProductItemFactory.create_batch(
#             2,
#             category=CategoryFactory(),
#             producer=ProducerFactory(),
#             discount=DiscountFactory(),
#         )


#     def test_create_order_view(self):
#         self.client.force_authenticate(user=self.user)

#         product_ids = ProductItem.objects.all().values_list('id', flat=True)

#         data = {
#             "product_items": {str(id_): 1 for id_ in product_ids},
#             "comment": "Here i check information",
#             "delivery_address": "Some addr",
#             "delivery_method": "Post",
#             "delivery_status": "In process",
#             "payment_method": "Cash",
#             "payment_status": "Paid",
#             "delivery_notif_required": False,
#             "delivery_notif_in_time": 1,
#             "delivery_notif_sent": False,
#             "use_cashback": True,
#             "promocode": "IEQTW6615",
#         }

#         response = self.client.post(reverse("create-order"), data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("id", response.data)
#         self.assertIn("result_price", response.data)
#         self.assertIn("result_number_of_items", response.data)
#         self.assertIn("user", response.data)


# class TestSingleProductItemView(APITestCase):
#     pass
