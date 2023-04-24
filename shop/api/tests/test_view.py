import pytest
from rest_framework.test import APITestCase
from django.urls import reverse
from .factories import CategoryFactory, RegistredUserFactory
import json



pytestmark = pytest.mark.django_db

EVERYTHING_EQUALS_NOT_NONE = type("omnieq", (), {"__eq__": lambda x, y: y is not None})()


class ApiTest(APITestCase):
    # fixtures = ["api/tests/fixtures_categories.json"]
    @classmethod
    def setUpTestData(cls):
        cls.categories = CategoryFactory.create_batch(3)
        cls.user = RegistredUserFactory(is_active=True, password="vbeobr30334")

    def test_categories_list_view(self):
        url = reverse("categories-all")
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data == [
            EVERYTHING_EQUALS_NOT_NONE,
            EVERYTHING_EQUALS_NOT_NONE,
            EVERYTHING_EQUALS_NOT_NONE,
        ]
        assert len(response.data) == 3


    def test_user_basket(self):
        url = reverse("login")
        data = {"user":{
            "phone": self.user.phone,
            "password": "vbeobr30334"
        }}
        json_data = json.dumps(data)
        token = "Bearer " + str(self.client.post(url, data=json_data, content_type="application/json").data["token"])[2:-1]

        self.client.credentials(HTTP_AUTHORIZATION=token)
        url = reverse("basket")
        response = self.client.get(url)

        assert response.status_code == 200
